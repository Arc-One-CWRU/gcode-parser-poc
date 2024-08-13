from ..test_base.test_base import TestSectionProcessorInterface, GCodeSection
from arcgcode.cura.settings import CuraMicerSettings
from arcgcode.processor.base.cura import END_OF_HEADER_SETTINGS_GRIFFIN, \
    END_OF_HEADER_SETTINGS_MARLIN
from dataclasses import fields
import unittest


class TestAddMicerSettings(TestSectionProcessorInterface, unittest.TestCase):
    """Tests for added post-processing script user-defined settings to the GCode file
    in the top-metadata.
    """

    def __init__(self, settings: CuraMicerSettings) -> None:
        super().__init__()
        self.settings = settings
    
    class Test(unittest.TestCase):
        def __init__(self, methodName: str, gcode_section: list[str], settings) -> None:
            super().__init__(methodName)
            self.gcode_section = gcode_section
            self.settings = settings

        def test_add_micer_settings(self):
            flag1 = "Generated with test did not run"
            flag2 = "Header settings test did not run"
            GENERATED_STRING = ";Generated with "
            i = 0
            while i < len(self.gcode_section):
                if self.gcode_section[i].startswith(GENERATED_STRING):
                    self.assertEqual(self.gcode_section[i][len(self.gcode_section[i])-11:], f" + Arc One\n")
                    flag1 = "Generated with test did run"
                elif (self.gcode_section[i].startswith(END_OF_HEADER_SETTINGS_MARLIN) or
                    self.gcode_section[i].startswith(END_OF_HEADER_SETTINGS_GRIFFIN)):
                    i += 2
                    self.assertEqual(";Arc One Settings\n", self.gcode_section[i])
                    flag2 = "Header settings test did run"
                    for field in fields(self.settings):
                        i+=1
                        settings_attr = field.name
                        settings_val = getattr(self.settings, settings_attr)
                        parsed_settings = f';{settings_attr} = {settings_val}\n'
                        self.assertEqual(parsed_settings, self.gcode_section[i])
                i += 1
            self.assertEqual("Generated with test did run", flag1)   
            self.assertEqual("Header settings test did run", flag2)

    def process(self, gcode_section: list[str]) -> list[str]:
        """Runs the test
        """
        self.gcode_section = gcode_section
        tests = [self.Test("test_add_micer_settings", gcode_section, self.settings)]
        return unittest.TestSuite(tests=tests)

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.TOP_COMMENT_SECTION