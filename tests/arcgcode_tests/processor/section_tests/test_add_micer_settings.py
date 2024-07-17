from ..test_base.test_base import TestSectionProcessorInterface, GCodeSection
from arcgcode.processor.base import version
from arcgcode.cura.settings import CuraMicerSettings
from arcgcode.processor.base.cura import END_OF_HEADER_SETTINGS_GRIFFIN, \
    END_OF_HEADER_SETTINGS_MARLIN
from dataclasses import fields
import unittest


class TestAddMicerSettings(TestSectionProcessorInterface, unittest.TestCase):
    """Adds the post-processing script user-defined settings to the GCode file
    in the top-metadata.
    """

    def __init__(self, settings: CuraMicerSettings) -> None:
        super().__init__()
        self.settings = settings
    
    class Test(unittest.TestCase):
        def __init__(self, methodName: str, gcode_section: list[str]) -> None:
            super().__init__(methodName)
            self.gcode_section = gcode_section

        def test_add_micer_settings(self):
            flag = False
            git_hash = version.ARCGCODE_VERSION
            for instruction in self.gcode_section:
                if git_hash in instruction:
                    flag = True
            
            self.assertTrue(flag)

    def process(self, gcode_section: list[str]) -> list[str]:
        """Reads the G-Code file buffer and does an action. It should return
        the desired G-Code string for that section.
        """
        self.gcode_section = gcode_section
        tests = [self.Test("test_add_micer_settings", gcode_section)]
        return unittest.TestSuite(tests=tests)

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.TOP_COMMENT_SECTION