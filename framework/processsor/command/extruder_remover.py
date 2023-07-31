import re
from ..base.base import CommandProcessorInterface


class G1ExtruderRemover(CommandProcessorInterface):
    """Removes the extruder argument in G1 commands.
    """

    def __init__(self) -> None:
        super().__init__()
        self.extruder_g1_matcher = re.compile(
            "([E][-+]?([0-9]*\.[0-9]*|[0-9]*))\w+")

    def process(self, gcode_instruction: str) -> str:
        """Matches a G-Code instruction. It should return
        the desired G-Code string for that line.
        """
        if not gcode_instruction.startswith("G1"):
            return gcode_instruction

        # Remove all extruder instructions in G1 commands
        new_g1 = self.extruder_g1_matcher.sub("", gcode_instruction)
        return new_g1
