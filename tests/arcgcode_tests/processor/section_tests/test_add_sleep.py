from ..test_base.test_base import TestSectionProcessorInterface, GCodeSection
from arcgcode.processor.base import version
import unittest


class TestAddSleep(TestSectionProcessorInterface, unittest.TestCase):
    """Adds sleep after each layer.
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
            (ds, s) = modf(self.sleep_time)
            # Converts into ms
            ms = int(ds*1000)
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
        tests = [self.Test("test_add_sleep", gcode_section, self.settings)]
        return unittest.TestSuite(tests=tests)

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION