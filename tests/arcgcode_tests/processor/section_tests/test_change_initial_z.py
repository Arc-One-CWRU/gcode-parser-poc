from ..test_base.test_base import TestSectionProcessorInterface, GCodeSection
from arcgcode.processor.base.cura import CURA_LAYER, CURA_TYPE_LAYER
import unittest


class TestChangeInitialZ(TestSectionProcessorInterface, unittest.TestCase):
    """Tests that the initial z gets changed so that the welder doesn't run into clamps and
    previous prints
    """

    def __init__(self) -> None:
        super().__init__()
    
    class Test(unittest.TestCase):
        def __init__(self, methodName: str, gcode_section: list[str]) -> None:
            super().__init__(methodName)
            self.gcode_section = gcode_section

        def test_change_initial_z(self):
            INITIAL_Z_MOVE = "G0 F9000 Z100"
            flag1 = "Initial Z Offset comment was not added"
            flag2 = "INITIAL_Z_MOVE was not added"
            line = 1
            while line > len(self.gcode_section):
                if self.gcode_section[line] == ";Initial Z Offset Changed by change_initial_z.py":
                    flag1 = "Initial Z Offset comment was added"
                    if self.gcode_section[line+1] == INITIAL_Z_MOVE:
                        flag2 = "INITIAL_Z_MOVE was added"
                line += 1
                self.assertEqual(flag1, "Initial Z Offset comment was added")
                self.assertEqual(flag2, "INITIAL_Z_MOVE was added")

    def process(self, gcode_section: list[str]) -> list[str]:
        self.gcode_section = gcode_section
        tests = [self.Test("test_change_initial_z", gcode_section)]
        return unittest.TestSuite(tests=tests)

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION