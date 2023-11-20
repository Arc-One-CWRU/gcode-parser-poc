from typing import List, Tuple
from .processor import CommandProcessorInterface, SectionProcessorInterface, \
    GCodeSection
from .processor.base.cura import END_OF_TOP_METADATA, END_OF_STARTUP_SCRIPT, \
    END_OF_GCODE, is_end_of_gcode_movements


class CuraGCodePipeline(object):
    """Applys each processor to Cura Engine G-Code files to generate a new WAAM
    compatible G-Code.
    """

    def __init__(self, section_processors: List[SectionProcessorInterface],
                 command_processor: List[CommandProcessorInterface]) -> None:
        self.section_processors = section_processors
        self.command_processors = command_processor

        # Divide section processors into the respective buckets
        self.top_metadata_processors: List[SectionProcessorInterface] = []
        self.startup_script_processors: List[SectionProcessorInterface] = []
        self.gcode_movements_processors: List[SectionProcessorInterface] = []
        self.end_script_processors: List[SectionProcessorInterface] = []
        self.bottom_comment_processors: List[SectionProcessorInterface] = []

        for processor in self.section_processors:
            self.append_processors(processor)

    def append_processors(self, processor: SectionProcessorInterface):
        if processor.section_type() is GCodeSection.TOP_COMMENT_SECTION:
            self.top_metadata_processors.append(processor)
        elif processor.section_type() is GCodeSection.STARTUP_SCRIPT_SECTION:
            self.startup_script_processors.append(processor)
        elif processor.section_type() is GCodeSection.GCODE_MOVEMENTS_SECTION:
            self.gcode_movements_processors.append(processor)
        elif processor.section_type() is GCodeSection.END_SCRIPT_SECTION:
            self.end_script_processors.append(processor)
        elif processor.section_type() is GCodeSection.BOTTOM_COMMENT:
            self.bottom_comment_processors.append(processor)
        else:
            err_msg = f"processor section_type {processor.section_type()} " + \
                        "is invalid"
            raise ValueError(err_msg)

    def process_commands(self, section_processed_file: list[str]) -> list[str]:
        """Ingests the section processed file and applies all of the command
        transforms line-by-line.
        """
        new_gcode: list[str] = []
        for gcode_line in section_processed_file:
            processed_line = gcode_line
            for cmd_processor in self.command_processors:
                processed_line = cmd_processor.process(processed_line)
            if not processed_line.endswith("\n"):
                processed_line = processed_line + "\n"
            new_gcode.append(processed_line)
        return new_gcode

    def read_section(self, gcode_data: list[str],
                     start_idx: int,
                     end_indicator: str) -> Tuple[list[str], int]:
        """Generic utility function for reading a section.

        Args:
            gcode_data: a list of the gcode commands. Each command should end
            with a new line.
            start_idx: the start of the section to process
            end_indicator: the start of a line that indicates the end of the
            section to process

        Returns:
            str: the section
            int: the index of the last element of the section processed
        """
        is_in_section = True
        section_contents: list[str] = []
        iter_idx = start_idx
        while is_in_section and iter_idx < len(gcode_data):
            curr_line = gcode_data[iter_idx]
            section_contents.append(curr_line)
            if curr_line.strip().startswith(end_indicator):
                is_in_section = False
            iter_idx += 1

        return section_contents, iter_idx-1

    # Apply Section Processors
    # Could refactor this.
    # I.e. ingest section end matcher and processors related to that section
    # Can get the section through the `Type` method

    def read_top_metadata(self, gcode_data: list[str],
                          start_idx: int) -> Tuple[list[str], int]:
        """Reads the top metadata comments.

        Returns the top metadata and the last index of the top metadata
        inclusive.

        So if the top metadata ends at index=2, then it will return index 2.
        """
        return self.read_section(gcode_data, start_idx, END_OF_TOP_METADATA)

    def read_startup_script(self, gcode_data: list[str],
                            start_idx: int) -> Tuple[list[str], int]:
        """Reads the startup script. Assumes that the top metadata has already
        been read.

        Returns the startup script section and the last index of the section
        inclusive.
        """
        return self.read_section(gcode_data, start_idx,
                                 END_OF_STARTUP_SCRIPT)

    def read_gcode_movements(self, gcode_data: list[str],
                             start_idx: int) -> Tuple[list[str], int]:
        """Reads the actual movement G-Code instructions.

        Returns the GCode movements section and the last index of the section
        inclusive.
        """
        # Similar to read_section except that it needs to check the next line
        # since the end indicator can occur multiple times throughout the
        # G-Code
        is_in_section = True
        section_contents: list[str] = []
        iter_idx = start_idx
        while is_in_section and iter_idx < len(gcode_data):
            curr_line = gcode_data[iter_idx]
            section_contents.append(curr_line)
            is_end = is_end_of_gcode_movements(curr_line, iter_idx, gcode_data)
            is_in_section = not is_end
            iter_idx += 1

        return section_contents, iter_idx-1

    def read_end_script(self, gcode_data: list[str],
                        start_idx: int) -> Tuple[list[str], int]:
        """Reads the end script.
        """
        return self.read_section(gcode_data, start_idx, END_OF_GCODE)

    def read_bottom_comment(self, gcode_data: list[str],
                            start_idx: int) -> Tuple[list[str], int]:
        """Reads the bottom comment. Can do so by reading the rest of the
        buffer.
        """
        return gcode_data[start_idx:], len(gcode_data) - 1

    def process(self, gcode_data: list[str]) -> list[str]:
        """Applies all of the transforms and returns the newly procesed WAAM
        compatible G-Code file string.
        """
        gcode_file: list[str] = []

        gcode_file.append(";Generated with ArcOne Post-Processing Script\n")
        gcode_file.append(";top metadata start\n")
        # Divide into sections
        # 1. Top Comment (Settings & Metadata)
        top_metadata, top_meta_end_idx = self.read_top_metadata(gcode_data,
                                                                0)
        for processor in self.top_metadata_processors:
            top_metadata = processor.process(top_metadata)
        gcode_file.extend(top_metadata)
        gcode_file.append(";top metadata end\n")

        # 2. Startup Script: Apply all start up script processors
        gcode_file.append(";startup script start\n")
        start_idx = top_meta_end_idx + 1
        startup_script, start_end_idx = self.read_startup_script(gcode_data,
                                                                 start_idx)
        for processor in self.startup_script_processors:
            startup_script = processor.process(startup_script)
        gcode_file.extend(startup_script)
        gcode_file.append(";startup script end\n\n")

        # # 3. G-Code Movements
        # TODO: Read layer by layer
        gcode_file.append(";gcode movements start\n")
        movements, move_end_idx = self.read_gcode_movements(gcode_data,
                                                            start_end_idx+1)
        for processor in self.gcode_movements_processors:
            movements = processor.process(movements)
        gcode_file.extend(movements)
        gcode_file.append(";gcode movements end\n\n")

        # 4. End Script: Apply all end script processors.
        gcode_file.append(";end script start\n")
        end_script, end_script_idx = self.read_end_script(gcode_data,
                                                          move_end_idx+1)
        for processor in self.end_script_processors:
            end_script = processor.process(end_script)
        gcode_file.extend(end_script)
        gcode_file.append(";end script end\n\n")

        # 5. Bottom Comment
        gcode_file.append(";bottom comment start\n")
        bottom_comment, _ = self.read_bottom_comment(gcode_data,
                                                     end_script_idx+1)
        gcode_file.extend(bottom_comment)
        gcode_file.append(";bottom comment end\n\n")

        new_gcode_file = self.process_commands(gcode_file)
        return new_gcode_file
