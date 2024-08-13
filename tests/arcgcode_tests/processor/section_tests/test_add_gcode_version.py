from ..test_base.test_base import TestSectionProcessorInterface, GCodeSection
from arcgcode.processor.base import version
import unittest


class TestAddGcodeVersion(TestSectionProcessorInterface, unittest.TestCase):
    """Tests that the micer settings were added to the GCode file.
    """

    def __init__(self) -> None:
        super().__init__()
    
    class Test(unittest.TestCase):
        def __init__(self, methodName: str, gcode_section: list[str]) -> None:
            super().__init__(methodName)
            self.gcode_section = gcode_section

        def test_add_gcode_version(self):
            """Test passes if git hash is in the gcode section
            """
            flag = False
            git_hash = version.ARCGCODE_VERSION
            for instruction in self.gcode_section:
                if git_hash in instruction:
                    flag = True
            
            self.assertTrue(flag)

    def process(self, gcode_section: list[str]) -> list[str]:
        """Runs the test
        """
        self.gcode_section = gcode_section
        tests = [self.Test("test_add_gcode_version", gcode_section)]
        return unittest.TestSuite(tests=tests)

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.TOP_COMMENT_SECTION
