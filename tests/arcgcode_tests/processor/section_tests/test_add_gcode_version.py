from ..test_base.test_base import TestSectionProcessorInterface, GCodeSection
from arcgcode.processor.base import version
import unittest


class TestAddGcodeVersion(TestSectionProcessorInterface, unittest.TestCase):
    """Adds the micer settings to GCode file.
    """

    def __init__(self) -> None:
        super().__init__()

    def test_add_gcode_version(self, gcode_section):
        flag = False
        git_hash = version.ARCGCODE_VERSION
        for instruction in gcode_section:
            if f"Git Commit Hash (Version): {git_hash})" in instruction:
                flag = True
        
        self.assertTrue(flag)

    def process(self, gcode_section: list[str]) -> list[str]:
        """Adds the git commit hash to the top of the G-Code files to
        differentiate versions
        """
        
        tests = self.test_add_gcode_version(gcode_section)
        return unittest.TestSuite(tests=tests)

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.TOP_COMMENT_SECTION
