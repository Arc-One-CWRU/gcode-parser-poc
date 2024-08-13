from ..test_base.test_base import TestSectionProcessorInterface, GCodeSection
import unittest


class TestPostHome(TestSectionProcessorInterface, unittest.TestCase):
    """Tests that the machine homes after print finish.
    """

    def __init__(self) -> None:
        super().__init__()
    
    class Test(unittest.TestCase):
        def __init__(self, methodName: str, gcode_section: list[str]) -> None:
            super().__init__(methodName)
            self.gcode_section = gcode_section

        def test_post_home(self):
            flag = False
            home_script = [
            "G91\n",
            "G1 Z100\n",
            "G90\n",
            "G28 XY\n",
            "G28 Z\n"
            ]
            i = 0
            while i < len(self.gcode_section):
                if "end script start" in self.gcode_section[i]:
                    try:
                        if self.gcode_section[i+1:i+6] == home_script:
                            flag = True
                    except Exception as e:
                        print(e)
                        i = len(self.gcode_section)
                i += 1
            self.assertTrue(flag)

    def process(self, gcode_section: list[str]) -> list[str]:
        """Runs the test
        """
        self.gcode_section = gcode_section
        tests = [self.Test("test_post_home", gcode_section)]
        return unittest.TestSuite(tests=tests)

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.END_SCRIPT_SECTION
