import io
from typing import List
from .processor import CommandProcessorInterface, SectionProcessorInterface, GCodeSection

# Cura specific constants.
END_OF_TOP_METADATA = ";Generated with"
END_OF_STARTUP_SCRIPT = ";LAYER_COUNT:"
END_OF_GCODE_MOVEMENTS = ";TIME_ELAPSED"
END_OF_GCODE = ";End of Gcode"


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
                raise ValueError(
                    f"processor section_type {processor.section_type()} is invalid")

    def process_commands(self, section_processed_file: str) -> str:
        """Ingests the section processed file and applies all of the command
        transforms line-by-line.
        """
        all_gcode_lines = section_processed_file.splitlines()
        new_gcode = ""
        for gcode_line in all_gcode_lines:
            processed_line = gcode_line
            for cmd_processor in self.command_processors:
                processed_line = cmd_processor.process(processed_line)
            new_gcode += processed_line + "\n"
        return new_gcode

    # Apply Section Processors
    # Could refactor this.
    # I.e. ingest section end matcher and processors related to that section
    # Can get the section through the `Type` method

    def read_top_metadata(self, file_buffer: io.TextIOWrapper) -> str:
        """Reads the top metadata comments.
        """
        is_metadata = True
        top_metadata = ""
        while is_metadata:
            curr_line = file_buffer.readline()
            top_metadata += curr_line
            if curr_line.startswith(END_OF_TOP_METADATA):
                is_metadata = False
        return top_metadata

    def read_startup_script(self, file_buffer: io.TextIOWrapper) -> str:
        """Reads the startup script. Assumes that the top metadata has already
        been read.
        """
        is_startup_script = True
        startup_script = ""
        while is_startup_script:
            curr_line = file_buffer.readline()
            startup_script += curr_line
            if curr_line.startswith(END_OF_STARTUP_SCRIPT):
                is_startup_script = False
        return startup_script

    def read_gcode_movements(self, file_buffer: io.TextIOWrapper) -> str:
        """Reads the actual movement G-Code instructions.
        """
        is_gcode_movement = True
        gcode_movement_instructions = ""
        while is_gcode_movement:
            curr_line = file_buffer.readline()
            gcode_movement_instructions += curr_line
            if curr_line.startswith(END_OF_GCODE_MOVEMENTS):
                is_gcode_movement = False
        return gcode_movement_instructions

    def read_end_script(self, file_buffer: io.TextIOWrapper) -> str:
        """Reads the end script.
        """
        is_end_script = True
        end_script = ""
        while is_end_script:
            curr_line = file_buffer.readline()
            end_script += curr_line
            if curr_line.startswith(END_OF_GCODE):
                is_end_script = False

        return end_script

    def read_bottom_comment(self, file_buffer: io.TextIOWrapper) -> str:
        """Reads the bottom comment. Can do so by reading the rest of the
        buffer.
        """
        return "".join(file_buffer.readlines())

    def process(self, file_buffer: io.TextIOWrapper) -> str:
        """Applies all of the transforms and returns the newly procesed WAAM
        compatible G-Code file string.
        """
        gcode_file = ""
        # Divide into sections
        # 1. Top Comment (Settings & Metadata)
        top_metadata = self.read_top_metadata(file_buffer=file_buffer)
        gcode_file += top_metadata + "\n"

        # 2. Startup Script: Apply all start up script processors
        gcode_file += ";startup script start\n"
        startup_script = self.read_startup_script(file_buffer=file_buffer)
        for processor in self.startup_script_processors:
            startup_script = processor.process(startup_script)
        gcode_file += startup_script
        gcode_file += ";startup script end\n\n"

        # 3. G-Code Movements
        # TODO: Read layer by layer
        gcode_file += ";gcode movements start\n"
        gcode_movements = self.read_gcode_movements(file_buffer=file_buffer)
        for processor in self.gcode_movements_processors:
            gcode_movements = processor.process(gcode_movements)
        gcode_file += gcode_movements
        gcode_file += ";gcode movements end\n\n"

        # 4. End Script: Apply all end script processors.
        gcode_file += ";end script start\n"
        end_script = self.read_end_script(file_buffer=file_buffer)
        for processor in self.end_script_processors:
            end_script = processor.process(end_script)
        gcode_file += end_script
        gcode_file += ";end script end\n\n"
        gcode_file += END_OF_GCODE + "\n"

        # 5. Bottom Comment
        gcode_file += ";bottom comment start\n"
        gcode_file += self.read_bottom_comment(file_buffer=file_buffer)
        gcode_file += ";bottom comment end\n\n"

        new_gcode_file = self.process_commands(gcode_file)
        return new_gcode_file
