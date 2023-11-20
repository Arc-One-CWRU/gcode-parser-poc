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

        for idx, instruction in enumerate(gcode_section):
            if instruction.startswith(CURA_LAYER):
                new_gcode_section.append(instruction)
                if skip_first:
                    skip_first = False
                    continue
                wait_instruction = f"{GCodes.WAIT.value} P2 S2\n"
                new_gcode_section.append(wait_instruction)
            # Only care about the end of the movements section.
            # Assumed that it is Cura.
            
            else:
                new_gcode_section.append(instruction)

        section_with_wait: list[str] = []
        for line in new_gcode_section:
            section_with_wait.append(line)

        return section_with_wait

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION
