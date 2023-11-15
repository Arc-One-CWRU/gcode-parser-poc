import re
from ..base import CommandProcessorInterface


class ChangeMovementRate(CommandProcessorInterface):
    """This processor will make sure that the user-provided movement rate (The
    feed rate per minute of the move between the starting point and ending
    point (if supplied))will be applied to every `G1` movement (movement with
    extrusion).

    The user-provided movement rate is measured in mm/minute.
    """

    def __init__(self, movement_rate: float) -> None:
        super().__init__()
        # Matches only the speed in a G1 F{SPEED} command.
        # Generated with ChatGPT:
        # (?<=G1 F)\d+
        self.g1_movement_matcher = re.compile(r"(?<=G1 F)\d+")
        self.movement_rate = movement_rate

    def process(self, gcode_instruction: str) -> str:
        """Reads the G-Code movements section and changes the speed in every
        G1 F command.
        """
        if gcode_instruction.startswith("G1 F"):
            new_g1 = self.g1_movement_matcher.sub(f"{self.movement_rate}",
                                                  gcode_instruction)
            return new_g1

        return gcode_instruction

