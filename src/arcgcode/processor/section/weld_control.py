import re
from ..base import SectionProcessorInterface, GCodeSection
from arcgcode.cura.gcodes import GCodes


class AllWelderControl(SectionProcessorInterface):
    """Adds instructions to control the welder from the GCode.
    """

    def __init__(self) -> None:
        super().__init__()
        self.is_start_of_layer_matcher = re.compile(r';[A-Z]')
    
    def parse_extruder_cmd(self, cmd: str) -> str:
        """Removes the extruder value the command.
        """
        e_index = cmd.find("E")
        short_line = cmd[e_index:len(cmd)]
        nums_in_line = re.findall(r"[-+]?(?:\d*\.*\d+)", short_line)
        e_value = nums_in_line[0]
        parsed_instruction = cmd.replace(f"E{e_value}", ";Removed extrusion in weld_control.py")
        return parsed_instruction

    def process(self, gcode_section: list[str]) -> list[str]:
        """Reads the G-Code file buffer and does an action. It should return
        the desired G-Code string for that section.
        """
        new_gcode_section: list[str] = []
        welder_is_on = False
        layer = 0
        bead = 1
        for i, instruction in enumerate(gcode_section):
            
            if instruction.startswith(";LAYER"):
                layer = int(instruction[7:])
                bead = 1
            # Edge Cases
            # Skip first line
            if i - 1 < 0:
                new_gcode_section.append(instruction)
                continue
            # Skip last line
            if i + 1 == len(gcode_section):
                new_gcode_section.append(instruction)
                new_gcode_section.append(GCodes.WELD_OFF.value + ", Added in weld_control.py")
                new_gcode_section.append("G4 P0" + " ;Added in weld_control.py")
                new_gcode_section.append(f"{GCodes.WELD_OFF_MESSAGE.value} L{layer} B{bead}\" ;Added in weld_control.py")
                bead += 1
                continue

            # Start the welder once when it's off and it encounters an
            # instruction that requires it to extrude.
            if " E" in instruction and not welder_is_on:
                welder_is_on = True
                new_gcode_section.append("G4 P0" + " ;Added in weld_control.py")
                new_gcode_section.append(GCodes.WELD_ON.value + ", Added in weld_control.py")
                new_gcode_section.append(f"{GCodes.WELD_ON_MESSAGE.value} L{layer} B{bead}\" ;Added in weld_control.py")
                parsed_instruction = self.parse_extruder_cmd(instruction)
                new_gcode_section.append(parsed_instruction)
            # If the welder is already on, extrude as usual
            elif " E" in instruction and welder_is_on:
                parsed_instruction = self.parse_extruder_cmd(instruction)
                new_gcode_section.append(parsed_instruction)
            # Turn the welder off the moment it encounters a non-extruding
            # instruction.
            elif " E" not in instruction and welder_is_on:
                welder_is_on = False
                new_gcode_section.append(GCodes.WELD_OFF.value + ", Added in weld_control.py")
                new_gcode_section.append("G4 P0" + " ;Added in weld_control.py")
                new_gcode_section.append(f"{GCodes.WELD_OFF_MESSAGE.value} L{layer} B{bead}\" ;Added in weld_control.py")
                bead += 1
                new_gcode_section.append(instruction)     
                
            # Just append any instructions where the welder is off and there
            # is no extruding.
            elif " E" not in instruction and not welder_is_on:
                new_gcode_section.append(instruction)

        return new_gcode_section

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION
