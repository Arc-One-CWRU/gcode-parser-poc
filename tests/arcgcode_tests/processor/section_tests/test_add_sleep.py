from ..test_base.test_base import TestSectionProcessorInterface, GCodeSection
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
            flag1 = "Sleep was not added"
            flag2 = "Sleep amount is incorrect"
            flag3 = "add_sleep comment was not added"
            if ";Added in wait_for_temp.py" not in self.gcode_section:
                line = 1
                while line < len(self.gcode_section):
                    if ";sleep_time = " in self.gcode_section[line]:
                        sleep_time = self.gcode_section[line][14,15]
                        #^not sure if I can get this since its in different g-code section
                    if ";LAYER:" in self.gcode_section[line] and "0" not in self.gcode_section[line][7]:
                        if "G4 S" in self.gcode_section[line+1]:
                            flag1 = "Sleep was added"
                        if self.gcode_section[line+1][4,5] == sleep_time:
                            flag2 = "Sleep amount is correct"
                        if self.gcode_section[line+2] == ";Added sleep in add_sleep.py\n":
                            flag3 = "add_sleep comment was added"
                    line =+ 1
            self.assertEqual(flag1, "Sleep was added")
            self.assertEqual(flag2, "Sleep amount is correct")
            self.assertEqual(flag3, "add_sleep comment was added")

        #if wait_for_temp not in gcode, check for added sleep, make sure sleep is correct amount,
        #and check for added comment

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