from arcgcode.cura.settings import CuraMicerSettings
from dataclasses import fields
from ..base import SectionProcessorInterface, GCodeSection
import os

class AddGcodeVersion(SectionProcessorInterface):
    """Adds the micer settings to GCode file.
    """

    def __init__(self) -> None:
        super().__init__()

    def process(self, gcode_section: list[str]) -> list[str]:
        """Adds the git commit hash to the top of the G-Code files to differentiate versions
        """
        git_hash = os.system("git rev-parse HEAD")
        gcode_version = f"Git Commit Hash (Version): {git_hash}\n"
        gcode_section.insert(0, gcode_version)
        return gcode_section

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.TOP_COMMENT_SECTION
