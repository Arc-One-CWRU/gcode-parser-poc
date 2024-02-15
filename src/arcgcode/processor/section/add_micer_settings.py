from arcgcode.cura.settings import CuraMicerSettings
from arcgcode.processor.base.cura import END_OF_HEADER_SETTINGS_GRIFFIN, \
    END_OF_HEADER_SETTINGS_MARLIN
from dataclasses import fields
from ..base import SectionProcessorInterface, GCodeSection


class AddMicerSettings(SectionProcessorInterface):
    """Adds the post-processing script user-defined settings to the GCode file
    in the top-metadata.
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
            GENERATED_STRING = ";Generated with "
            if instruction.startswith(GENERATED_STRING):
                new_gcode_section.append(f"{instruction.strip()} + Arc One\n")
            elif (instruction.startswith(END_OF_HEADER_SETTINGS_MARLIN) or
                  instruction.startswith(END_OF_HEADER_SETTINGS_GRIFFIN)):
                new_gcode_section.append(instruction + "\n;Arc One Settings\n")
                # Iterate over the attributes of the dataclass
                for field in fields(self.settings):
                    settings_attr = field.name
                    settings_val = getattr(self.settings, settings_attr)
                    parsed_settings = f';{settings_attr} = {settings_val}\n'
                    new_gcode_section.append(parsed_settings)
            else:
                new_gcode_section.append(instruction)
        wait_val = getattr(self.settings, "wait_for_temp")
        new_gcode_section.append(f"M568 P7 S{wait_val}")
        return new_gcode_section

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.TOP_COMMENT_SECTION
