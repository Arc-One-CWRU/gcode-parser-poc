from ..base import SectionProcessorInterface, GCodeSection
from arcgcode.cura.gcodes import GCodes
from arcgcode.processor.base.cura import CURA_LAYER


class AddPause(SectionProcessorInterface):
    """Adds sleep after each layer.
    """

    def __init__(self) -> None:
        super().__init__()

    def process(self, gcode_section: list[str]) -> list[str]:
        """Reads the G-Code file buffer and does an action. It should return
        the desired G-Code string for that section.
        """

        new_gcode_section: list[str] = []

        skip_first = True
        for instruction in gcode_section:
            new_gcode_section.append(instruction)
            if instruction.startswith(CURA_LAYER):
                if skip_first:
                    skip_first = False
                    continue
                sleep_instruction = f"{GCodes.PAUSE.value}\n"
                new_gcode_section.append(sleep_instruction + ";Added in add_pause_after_layer.py")
        return new_gcode_section
       
    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION
