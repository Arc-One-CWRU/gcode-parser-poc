from ..test_base.test_base import TestSectionProcessorInterface, GCodeSection
from arcgcode.processor.base import version
import unittest


class TestEnd(TestSectionProcessorInterface, unittest.TestCase):
    """Replaces the Cura end script with our own.
    """

    def __init__(self) -> None:
        super().__init__()
    
    class Test(unittest.TestCase):
        def __init__(self, methodName: str, gcode_section: list[str]) -> None:
            super().__init__(methodName)
            self.gcode_section = gcode_section

        def test_add_gcode_version(self):
            flag = False
            git_hash = version.ARCGCODE_VERSION
            for instruction in self.gcode_section:
                if git_hash in instruction:
                    flag = True
            
            self.assertTrue(flag)

    def process(self, gcode_section: list[str]) -> list[str]:
        """Replaces the Cura end script with our own.
        """
        end_script = [
            ";End Script Added in end.py"
            "M42 P1 S0; Turn off the welder\n",
            "G0 F20000 Z60; Raises the welding tip, quickly (F sets speed)\n"
        ]

        return end_script

    def section_type(self) -> GCodeSection:
        return GCodeSection.END_SCRIPT_SECTION
