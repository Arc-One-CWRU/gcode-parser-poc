from ..test_base.test_base import TestSectionProcessorInterface, GCodeSection
from arcgcode.processor.base import version
import unittest


class TestPostHome(TestSectionProcessorInterface, unittest.TestCase):
    """Homes the machine after print finish.
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
            "G91\n"
            "G1 Z100\n",
            "G90\n",
            "G28 XY\n",
            "G28 Z"
            ]
            if home_script in self.gcode_section:
                flag = True
            
            self.assertTrue(flag)

    def process(self, gcode_section: list[str]) -> list[str]:
        """Homes the machine after print finish.
        """
        self.gcode_section = gcode_section
        tests = [self.Test("test_post_home", gcode_section)]
        return unittest.TestSuite(tests=tests)

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.END_SCRIPT_SECTION
