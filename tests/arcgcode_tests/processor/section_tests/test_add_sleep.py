from ..test_base.test_base import TestSectionProcessorInterface, GCodeSection
from math import modf
import unittest


class TestAddSleep(TestSectionProcessorInterface, unittest.TestCase):
    """Tests for added sleep after each layer.
    """

    def __init__(self, sleep_time: float) -> None:
        super().__init__()
        self.sleep_time = sleep_time
    
    class Test(unittest.TestCase):
        def __init__(self, methodName: str, gcode_section: list[str], sleep_time) -> None:
            super().__init__(methodName)
            self.gcode_section = gcode_section
            self.sleep_time = sleep_time

        def test_add_sleep(self):
            flag1 = "Sleep was not added"
            flag2 = "Sleep amount is incorrect"
            flag3 = "add_sleep comment was not added"
            (ds, s) = modf(self.sleep_time)
            # Converts into ms
            ms = int(ds*1000)
            line = 1
            while line < len(self.gcode_section):
                if ";LAYER:" in self.gcode_section[line] and "0" not in self.gcode_section[line][7]:
                    if "G4 S" in self.gcode_section[line+1]:
                        flag1 = "Sleep was added"
                    if str(int(s)) in self.gcode_section[line+1] and str(ms) in self.gcode_section[line+1]:
                        flag2 = "Sleep amount is correct"
                    if self.gcode_section[line+2] == ";Added sleep in add_sleep.py\n":
                        flag3 = "add_sleep comment was added"
                line += 1
            self.assertEqual(flag1, "Sleep was added")
            self.assertEqual(flag2, "Sleep amount is correct")
            self.assertEqual(flag3, "add_sleep comment was added")

    def process(self, gcode_section: list[str]) -> list[str]:
        """Reads the G-Code file buffer and does an action. It should return
        the desired G-Code string for that section.
        """
        self.gcode_section = gcode_section
        tests = [self.Test("test_add_sleep", gcode_section, self.sleep_time)]
        return unittest.TestSuite(tests=tests)

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION