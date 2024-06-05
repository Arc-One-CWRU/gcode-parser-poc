from ..base import SectionProcessorInterface, GCodeSection
from arcgcode.cura.gcodes import GCodes
from arcgcode.processor.base.cura import CURA_LAYER


class AddPause(SectionProcessorInterface):
    """Adds a pause after each layer
    """

    def __init__(self) -> None:
        super().__init__()

    def process(self, gcode_section: list[str]) -> list[str]:
        """Adds a pause after each layer
        """
        # Sanity check, just in case there's an extra new line at the end of
        # the section for some reas

        new_gcode_section: list[str] = []

        skip_first = True
        for idx, instruction in enumerate(gcode_section):
            if instruction.startswith(CURA_LAYER):
                new_gcode_section.append(instruction)
                if skip_first:
                    skip_first = False
                    continue
                sleep_instruction = f"{GCodes.PAUSE.value}\n"
                new_gcode_section.append(sleep_instruction)
            # Only care about the end of the movements section.
            # Assumed that it is Cura.
            else:
                new_gcode_section.append(instruction)
        return new_gcode_section
       
    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION
