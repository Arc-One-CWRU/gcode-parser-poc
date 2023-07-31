import io
from typing import List
from .processsor import CommandProcessorInterface, SectionProcessorInterface

END_OF_STARTUP_SCRIPT = ";LAYER_COUNT:"
END_OF_GCODE = ";End of Gcode"
END_OF_TOP_METADATA = ";Generated with"


class GCodePipeline(object):
    """Applys each processor to the G-Code files to generate a new WAAM
    compatible G-Code.
    """

    def __init__(self, section_processors: List[SectionProcessorInterface],
                 command_processor: List[CommandProcessorInterface]) -> None:
        self.section_processor = section_processors
        self.command_processor = command_processor

    def process_commands(self, section_processed_file: str) -> str:
        """Ingests the section processed file and applies all of the command
        transforms line-by-line.
        """
        all_gcode_lines = section_processed_file.splitlines()
        new_gcode = ""
        for gcode_line in all_gcode_lines:
            processed_line = gcode_line
            for cmd_processor in self.command_processor:
                processed_line = cmd_processor.process(processed_line)
            new_gcode += processed_line + "\n"
        return new_gcode

    # Apply Section Processors

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

    def process(self, file_buffer: io.TextIOWrapper) -> str:
        """Applies all of the transforms and returns the newly procesed WAAM
        compatible G-Code file string.
        """
        gcode_file = ""
        # Divide into sections
        # 1. Top Comment (Settings & Metadata)
        top_metadata = self.read_top_metadata(file_buffer=file_buffer)
        gcode_file += top_metadata + "\n"

        # 2. Startup Script
        gcode_file += self.read_startup_script(file_buffer=file_buffer) + "\n"

        new_gcode_file = self.process_commands(gcode_file)
        return new_gcode_file
