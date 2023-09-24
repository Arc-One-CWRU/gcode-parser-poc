import re
from ..base import SectionProcessorInterface, GCodeSection
from arcgcode.cura.gcodes import GCodes


class AllWelderControl(SectionProcessorInterface):
    """Adds instructions to control the welder from the GCode.
    """

    def __init__(self) -> None:
        super().__init__()
        self.is_start_of_layer_matcher = re.compile(r';[A-Z]')

    def process(self, gcode_section: str) -> str:
        """Reads the G-Code file buffer and does an action. It should return
        the desired G-Code string for that section.
        """
        new_gcode_section = ""
        seen_e = False
        instructions = gcode_section.splitlines(True)
        for i, instruction in enumerate(instructions):
            # Edge Cases
            if i - 1 < 0:
                new_gcode_section += instruction
                continue
            if i + 1 == len(instructions):
                new_gcode_section += instruction
                continue

            if " E" in instruction and not seen_e:
                seen_e = True
                new_gcode_section += GCodes.WELD_ON.value 
                e_index = instruction.find("E")
                short_line = instruction[e_index:len(instruction)]
                nums_in_line = re.findall(r"[-+]?(?:\d*\.*\d+)", short_line)
                e_value = nums_in_line[0]
                new_gcode_section += instruction.replace(f"E{e_value}", "")

            elif " E" in instruction and seen_e:
                # I'm not sure what this really does? XD
                e_index = instruction.find("E")
                short_line = instruction[e_index:len(instruction)]
                nums_in_line = re.findall(r"[-+]?(?:\d*\.*\d+)", short_line)
                e_value = nums_in_line[0]
                new_gcode_section += instruction.replace(f"E{e_value}", "")
            elif " E" not in instruction and seen_e:
                seen_e = False
                new_gcode_section += GCodes.WELD_OFF.value 
            elif " E" not in instruction and not seen_e:
                new_gcode_section += instruction
        return new_gcode_section

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION
