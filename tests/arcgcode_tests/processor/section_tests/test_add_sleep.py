from ..test_base.test_base import TestSectionProcessorInterface, GCodeSection
from arcgcode.processor.base import version
import unittest


class TestAddSleep(TestSectionProcessorInterface, unittest.TestCase):
    """Adds sleep after each layer.
    """

    def __init__(self) -> None:
        super().__init__()
    
    class Test(unittest.TestCase):
        def __init__(self, methodName: str, gcode_section: list[str]) -> None:
            super().__init__(methodName)
            self.gcode_section = gcode_section

        def test_add_sleep(self):
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
        tests = [self.Test("test_add_sleep", gcode_section)]
        return unittest.TestSuite(tests=tests)

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION