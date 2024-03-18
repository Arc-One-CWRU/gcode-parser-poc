from ..base import SectionProcessorInterface, GCodeSection
from math import modf
from arcgcode.cura.gcodes import GCodes
from arcgcode.processor.base.cura import CURA_LAYER


class WaitForTemp(SectionProcessorInterface):
    """Adds command to wait for designated temperature after each layer before continueing.
    """

    def __init__(self) -> None:
        super().__init__()
        #self.wait_for_temp = wait_for_temp

    def process(self, gcode_section: list[str]) -> list[str]:
        """Reads the G-Code file buffer and does an action. It should return
        the desired G-Code string for that section.
        """
        new_gcode_section: list[str] = []
        skip_first = True
        skip_pause = False
        for i, instruction in enumerate(gcode_section):
            if skip_pause:
                skip_pause = False
                continue
            if instruction.startswith(CURA_LAYER):
                new_gcode_section.append(instruction)
                if skip_first:
                    skip_first = False
                    continue
                
                x_offset = 72
                y_offset = 74
                z_offset = 40
                new_gcode_section.append("G91")
                new_gcode_section.append(f"G1 Z{z_offset}")
                new_gcode_section.append(f"G1 X{x_offset} Y{y_offset}")
                new_gcode_section.append("G4 P0")
                new_gcode_section.append("M291 P\"Interpass Start\"")
                new_gcode_section.append(f"{GCodes.INTERPASS_MACRO.value}")
                
                new_gcode_section.append("G4 P0")
                new_gcode_section.append("M291 P\"Interpass End\"")
                if gcode_section[i+1].startswith("M226"):
                    new_gcode_section.append("M226")
                    skip_pause = True
                new_gcode_section.append(f"G1 X-{x_offset} Y-{y_offset}")
                new_gcode_section.append(f"G1 Z-{z_offset}")
                new_gcode_section.append("G90")
                # num = 3
                # changed_movement = new_gcode_section[len(new_gcode_section)-num]
                
                # x_index = changed_movement.find("X")
                # y_index = changed_movement.find("Y")
                # z_index = changed_movement.find("Z")
                # offset = 75
                
                # new_x = str(float(changed_movement[x_index+1:y_index-1])+offset)
                # new_y = str(float(changed_movement[y_index+1:z_index-1])+offset+10)
                # new_z = str(float(changed_movement[z_index+1:]) + 20)
                
                # temp = f"{changed_movement[:x_index+1]}{new_x} Y{new_y} Z{new_z}"
                # print(f"before: {new_gcode_section[len(new_gcode_section)-num]}after: {temp}")
                # new_gcode_section[len(new_gcode_section)-num] = temp
                
                # wait_instruction = f"{GCodes.INTERPASS_MACRO.value}"
                # new_gcode_section.append(wait_instruction)
            # Only care about the end of the movements section.
            # Assumed that it is Cura.
            else:
                new_gcode_section.append(instruction)

        return new_gcode_section

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION
