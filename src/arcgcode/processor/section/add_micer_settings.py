from arcgcode.cura.settings import CuraMicerSettings
from dataclasses import fields
from ..base import SectionProcessorInterface, GCodeSection


class AddMicerSettings(SectionProcessorInterface):
    """Adds the micer settings to GCode file.
    """

    def __init__(self, settings: CuraMicerSettings) -> None:
        super().__init__()
        self.settings = settings

    def process(self, gcode_section: list[str]) -> list[str]:
        """Reads the G-Code file buffer and does an action. It should return
        the desired G-Code string for that section.
        """
        new_gcode_section: list[str] = []
        for instruction in gcode_section:
            GENERATED_STRING = ";Generated with Cura_SteamEngine 5.4.0"
            if instruction.startswith(GENERATED_STRING):
                new_gcode_section.append(f"{GENERATED_STRING} + Micer\n")
            elif instruction.startswith(";MAXZ:"):
                new_gcode_section.append(instruction + "\n;Micer Settings\n")
                # Iterate over the attributes of the dataclass
                for field in fields(self.settings):
                    settings_attr = field.name
                    settings_val = getattr(self.settings, settings_attr)
                    parsed_settings = f';{settings_attr} = {settings_val}\n'
                    new_gcode_section.append(parsed_settings)
            else:
                new_gcode_section.append(instruction)

        return new_gcode_section

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION
