import re
from math import ceil
import numpy as np
from ..base import SectionProcessorInterface, GCodeSection


class RotateStartLayerPrint(SectionProcessorInterface):
    """Rotates the start layer by the specified amount.
    """

    def __init__(self, rotate_amount: float) -> None:
        super().__init__()
        self.rotate_amount = rotate_amount

    def process(self, gcode_section: str) -> str:
        """Reads the G-Code file buffer and does an action. It should return
        the desired G-Code string for that section.
        """
        speed = -1
        layer_count = -1
        start_wall = False
        line_count = 0
        gotten_speed = False
        new_gcode_section = ""
        wall_lines: list[str] = []
        instructions = gcode_section.splitlines(True)
        for instruction in instructions:
            if instruction.startswith(";LAYER:"):
                new_gcode_section += instruction
                layer_count += 1
            elif instruction.startswith(";TYPE:WALL-OUTER"):
                start_wall = True
                line_count = 0
                wall_lines = []
                gotten_speed = False
                new_gcode_section += instruction
            elif " E" not in instruction and start_wall:
                first_wall_line = True
                start_wall = False
                # Splits and rotate chunks
                top_num = layer_count % self.rotate_amount
                percentage = top_num / self.rotate_amount

                lines_moved = ceil(percentage*line_count)

                rotated_lines = np.roll(wall_lines, lines_moved)
                for wall_line in rotated_lines:
                    moved_comment = f" ;Moved {lines_moved} lines\n"
                    no_new_line = str(wall_line).replace("\n", "")

                    if first_wall_line:
                        first_line = no_new_line.replace(" ", f" F{speed} ", 1)
                        first_wall_line = False
                        new_gcode_section += first_line + moved_comment
                        continue

                    new_gcode_section += no_new_line + moved_comment

                new_gcode_section += instruction
            elif start_wall:
                line_count += 1

                if instruction.startswith("G1 F") and not gotten_speed:
                    gotten_speed = True
                    # Gets Speed value out of a instruction
                    speed = re.findall(r"[-+]?(?:\d*\.*\d+)", instruction)[1]
                    generic_line = instruction.replace(f"F{speed} ", "")
                    wall_lines.append(generic_line)
                    continue

                wall_lines.append(instruction)
            else:
                new_gcode_section += instruction

        return new_gcode_section

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION
