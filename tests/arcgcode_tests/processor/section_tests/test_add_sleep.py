from ..test_base.test_base import TestSectionProcessorInterface, GCodeSection
from math import modf
from arcgcode.cura.gcodes import GCodes
from arcgcode.processor.base.cura import CURA_LAYER, END_OF_GCODE_MOVEMENTS, \
    find_end_of_gcode_movements_idx
import unittest


class TestAddSleep(TestSectionProcessorInterface, unittest.TestCase):
    """Tests for added sleep after each layer.
    """

    def __init__(self, settings) -> None:
        super().__init__()
        self.settings = settings
    
    class Test(unittest.TestCase):
        def __init__(self, methodName: str, gcode_section: list[str], settings) -> None:
            super().__init__(methodName)
            self.gcode_section = gcode_section
            self.settings = settings

        def test_add_sleep(self):
            ""
            #Incomplete but seems to not be used in gcode, check that add_sleep.py
            #is correctly adding comments/adding sleep

    def process(self, gcode_section: list[str]) -> list[str]:
        """Reads the G-Code file buffer and does an action. It should return
        the desired G-Code string for that section.
        """
        self.gcode_section = gcode_section
        tests = [self.Test("test_add_sleep", gcode_section, self.settings)]
        return unittest.TestSuite(tests=tests)

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION