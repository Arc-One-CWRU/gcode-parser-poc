import io
from typing import List
from .processsor import CommandProcessorInterface, SectionProcessorInterface


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

    def process(self, file_buffer: io.TextIOWrapper) -> str:
        """Applies all of the transforms and returns the newly procesed WAAM
        compatible G-Code file string.
        """
        # TODO: Use section transforms instead
        gcode_file = "".join(file_buffer.readlines())
        new_gcode_file = self.process_commands(gcode_file)
        return new_gcode_file
