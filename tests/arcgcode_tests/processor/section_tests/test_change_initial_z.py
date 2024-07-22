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
            flag1 = "Initial Z Offset comment was added in layer 0"
            flag2 = "INITIAL_Z_MOVE was added in layer 0"
            flag3 = "Initial Z Offset comment was not added in layer 0"
            flag4 = "INITIAL_Z_MOVE was not added in layer 0"
            flag5 = "Desired Z was removed"
            line = 1
            while line > len(self.gcode_section):
                if self.gcode_section[line] == ";LAYER:0":
                    layer0_start = line
                if self.gcode_section[line] == ";LAYER:1":
                    layer0_end = line-1
                line += 1
                layer0 = self.gcode_section[layer0_start:layer0_end]

            for line in layer0:
                if line == "Initial Z Offset Changed by change_initial_z.py":
                    flag3 = "Initial Z Offset comment was added in layer 0"
                if line == INITIAL_Z_MOVE:
                    flag4 = "INITIAL_Z_MOVE was added in layer 0"
                if line.startswith("G0"):
                    if ("X" in line or "Y" in line) and "Z" in line:
                        flag5 = "Desired Z was not removed"
                if ";Removed Z in change_initial_z.py" in line and "Z" not in line:
                    flag6 = "Removed Z comment was added and Z was removed"
                if ";Removed Z in change_initial_z.py" in line and "Z" not in line:
                    flag6 = "Removed Z comment was added and Z was removed"
                self.assertEqual(flag3, "Initial Z Offset comment was added in layer 0")
                self.assertEqual(flag4, "INITIAL_Z_MOVE was added in layer 0")
                self.assertEqual(flag5, "Desired Z was removed")

            for line in self.gcode_section:
                if line == "Initial Z Offset Changed by change_initial_z.py":
                    flag1 = "Initial Z Offset comment was added outside of layer 0"
                if line == INITIAL_Z_MOVE:
                    flag2 = "INITIAL_Z_MOVE was added outside of layer 0"
                self.assertEqual(flag1, "Initial Z Offset comment was added in layer 0")
                self.assertEqual(flag2, "INITIAL_Z_MOVE was added in layer 0")
                

            # flag1 = "Initial Z Offset comment was not added"
            # flag2 = "INITIAL_Z_MOVE was not added"
            # line = 1
            # while line > len(self.gcode_section):
            #     if self.gcode_section[line] == ";Initial Z Offset Changed by change_initial_z.py":
            #         flag1 = "Initial Z Offset comment was added"
            #         if self.gcode_section[line+1] == INITIAL_Z_MOVE:
            #             flag2 = "INITIAL_Z_MOVE was added"
            #     line += 1
            #     self.assertEqual(flag1, "Initial Z Offset comment was added")
            #     self.assertEqual(flag2, "INITIAL_Z_MOVE was added")

    def process(self, gcode_section: list[str]) -> list[str]:
        self.gcode_section = gcode_section
        tests = [self.Test("test_change_initial_z", gcode_section)]
        return unittest.TestSuite(tests=tests)

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION