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
        self.extruder_arg_matcher = re.compile(
            r"(\s[E][-+]?([0-9]*\.[0-9]*))")

    def should_skip(self, gcode_instruction: str) -> bool:
        """Checks if the given G-Code instruction should be skipped.

        Args:
            gcode_instruction (str): The G-Code instruction to check.

        Returns:
            bool: True if the instruction should be skipped.
        """
        if len(gcode_instruction.strip()) == 0:
            return True

        is_comment = gcode_instruction.startswith(";")
        if is_comment:
            return True

        # Just remove the extruder from every G1 command.
        # Welder control relies on the extruder value, so we should never
        # call this processor before the AllWelderControl
        if gcode_instruction.strip().startswith("G1"):
            return False

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
        contains_comment = len(split_instructions) > 1
        if contains_comment:
            actual_gcode_cmd = split_instructions[0]
            new_g1 = self.extruder_arg_matcher.sub("", actual_gcode_cmd)
            # Append comment to parsed gcode command
            return new_g1 + ";" + "".join(split_instructions[1:])
        
        # No comment after instruction
        new_g1 = self.extruder_arg_matcher.sub("", gcode_instruction)
        return new_g1
