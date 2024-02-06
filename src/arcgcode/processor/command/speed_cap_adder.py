import re
from ..base import CommandProcessorInterface


class SpeedCapAdder(CommandProcessorInterface):
    """This processor will make sure that the user-provided movement rate (The
    feed rate per minute of the move between the starting point and ending
    point (if supplied))will be applied to every `G1` movement (movement with
    extrusion).

    The user-provided movement rate is measured in mm/minute.
    """

    def __init__(self) -> None:
        super().__init__()
        # Matches only the speed in a G1 F{SPEED} command.
        # Generated with ChatGPT:
        # (?<=G1 F)\d+
        
    def process(self, gcode_instruction: str) -> str:
        """Reads the G-Code movements section and changes the speed in every
        G1 F command.
        """
        new_gcode_instruction = ""
        if gcode_instruction.startswith("G1 F"):
            i = 4
            while gcode_instruction[i].isnumeric():
                i += 1
            if int(gcode_instruction[4:i]) > 1000:
                new_gcode_instruction = gcode_instruction[0:4] + "1000" + gcode_instruction[i:]
            else:
                new_gcode_instruction = gcode_instruction
        else:
            new_gcode_instruction = gcode_instruction

        return new_gcode_instruction
