from ..test_base.test_base import TestSectionProcessorInterface, GCodeSection
import unittest


class TestChangeG0ToG1(TestSectionProcessorInterface, unittest.TestCase):
    """Tests if G0 becomes G1
    """

    def __init__(self) -> None:
        super().__init__()
    
    class Test(unittest.TestCase):
        def __init__(self, methodName: str, gcode_section: list[str]) -> None:
            super().__init__(methodName)
            self.gcode_section = gcode_section

        def test_change_G0_to_G1(self):
            flag = "G0 did get replaced"
            for line in self.gcode_section:
                if line.startswith("G0"):
                    flag = "G0 did not get replaced"
            self.assertEqual(flag, "G0 did get replaced")

    def process(self, gcode_section: list[str]) -> list[str]:
        """Reads the G-Code file buffer and does an action. It should return
        the desired G-Code string for that section.
        """
        self.gcode_section = gcode_section
        tests = [self.Test("test_change_G0_to_G1", gcode_section)]
        return unittest.TestSuite(tests=tests)

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION