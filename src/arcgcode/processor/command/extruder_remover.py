import re
from ..base.base import CommandProcessorInterface


class ExtruderRemover(CommandProcessorInterface):
    """Removes the extruder argument in commands that have Xnnn, Ynnn, Znnn,
    Ennn as arguments.

    These commands include but are not limited to:
    G0, G1, G2, G3, G92, M566
    """

    def __init__(self) -> None:
        super().__init__()
        self.extruder_g1_matcher = re.compile(
            r"([E][-+]?([0-9]*\.[0-9]*|[0-9]*))\w+")

    def should_skip(self, gcode_instruction: str) -> bool:
        """Checks if the given G-Code instruction should be skipped.

        Args:
            gcode_instruction (str): The G-Code instruction to check.

        Returns:
            bool: True if the instruction should be skipped.
        """
        is_comment = gcode_instruction.startswith(";")
        if is_comment:
            return True

        skip_line = "X" not in gcode_instruction and \
            "Y" not in gcode_instruction and \
            "Z" not in gcode_instruction and " E" in gcode_instruction

        return skip_line

    def process(self, gcode_instruction: str) -> str:
        """Matches a G-Code instruction. It should return
        the desired G-Code string for that line.
        """
        if self.should_skip(gcode_instruction):
            return gcode_instruction

        # Remove all extruder instructions in G1 commands
        # Handle case where there is a comment after the instruction
        split_instructions = gcode_instruction.split(";")
        actual_gcode_cmd = split_instructions[0]
        new_g1 = self.extruder_g1_matcher.sub("", actual_gcode_cmd)
        return new_g1 + ";".join(split_instructions[1:])
