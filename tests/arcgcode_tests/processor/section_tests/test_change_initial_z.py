from ..test_base.test_base import TestSectionProcessorInterface, GCodeSection
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
            flag1 = "No Initial Z Offset comment was added outside of layer 0"
            flag2 = "No INITIAL_Z_MOVE was added outside of layer 0"
            flag3 = "No removed Z comments were added outside of layer 0"
            flag4 = "Initial Z Offset comment was not added in layer 0"
            flag5 = "INITIAL_Z_MOVE was not added in layer 0"
            flag6 = "Desired Z was removed"
            flag7 = "Removed Z comment was not added or Z was not removed"
            layer0_start = 0
            layer0_end = 0
            layer0 = []
            line = 0
            while line < len(self.gcode_section):
                if self.gcode_section[line] == ";LAYER:0\n":
                    layer0_start = line
                if self.gcode_section[line] == ";LAYER:1\n":
                    layer0_end = line
                line += 1
                layer0 = self.gcode_section[layer0_start:layer0_end]
                
            for line in self.gcode_section:
                if line == ";Initial z Offset Changed by change_initial_z.py\n" and line not in layer0:
                    flag1 = "An Initial Z Offset comment was added outside of layer 0"
                if (INITIAL_Z_MOVE in line or "G1F9000 Z100" in line) and line not in layer0:
                    flag2 = "An INITIAL_Z_MOVE was added outside of layer 0"
                if ";Removed z in change_initial_z.py" in line and line not in layer0:
                    flag3 = "A Removed Z comment was added outside of layer 0, check line for an undesired Z removal"

            for line in layer0:
                if line == ";Initial z Offset Changed by change_initial_z.py\n":
                    flag4 = "Initial Z Offset comment was added in layer 0"
                if INITIAL_Z_MOVE in line or "G1F9000 Z100" in line:
                    flag5 = "INITIAL_Z_MOVE was added in layer 0"
                if line.startswith("G0"):
                    if ("X" in line or "Y" in line) and "Z" in line:
                        flag6 = "Desired Z was not removed"
                if ";Removed z in change_initial_z.py" in line and "Z" not in line:
                    flag7 = "Removed Z comment was added and Z was removed"
                    
            self.assertEqual(flag1, "No Initial Z Offset comment was added outside of layer 0")
            self.assertEqual(flag2, "No INITIAL_Z_MOVE was added outside of layer 0")
            self.assertEqual(flag3, "No removed Z comments were added outside of layer 0")
            self.assertEqual(flag4, "Initial Z Offset comment was added in layer 0")
            self.assertEqual(flag5, "INITIAL_Z_MOVE was added in layer 0")
            self.assertEqual(flag6, "Desired Z was removed")
            self.assertEqual(flag7, "Removed Z comment was added and Z was removed")

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