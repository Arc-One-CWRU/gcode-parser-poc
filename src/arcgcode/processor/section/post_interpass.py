from ..base import SectionProcessorInterface, GCodeSection
from arcgcode.cura.background_settings import BackgroundSettings
from arcgcode.cura.gcodes import GCodes


class PostInterpass(SectionProcessorInterface):
    """Adds the micer settings to GCode file.
    """

    def __init__(self) -> None:
        super().__init__()

    def process(self, gcode_section: list[str]) -> list[str]:
        """Adds the git commit hash to the top of the G-Code files to
        differentiate versions
        """

        gcode_section.insert(0, "G90")
        gcode_section.insert(0, f"G1 Z-{BackgroundSettings.Z_OFFSET}")
        gcode_section.insert(0, f"G1 X-{BackgroundSettings.X_OFFSET} Y-{BackgroundSettings.Y_OFFSET}")
        gcode_section.insert(0, "M291 P\"Interpass End\"")
        gcode_section.insert(0, "G4 P0")
        gcode_section.insert(0, f"{GCodes.INTERPASS_MACRO.value}")
        gcode_section.insert(0, "M291 P\"Interpass Start\"")
        gcode_section.insert(0, "G4 P0")
        gcode_section.insert(0, f"G1 X{BackgroundSettings.X_OFFSET} Y{BackgroundSettings.Y_OFFSET}")
        gcode_section.insert(0, f"G1 Z{BackgroundSettings.Z_OFFSET}")
        gcode_section.insert(0, "G91")

        return gcode_section

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.END_SCRIPT_SECTION
