from ..test_base.test_base import TestSectionProcessorInterface, GCodeSection
import unittest


class TestMoveUpZ(TestSectionProcessorInterface, unittest.TestCase):
    """Test that post-processor translates all commands with 
       Z arguments up by the (weld_gap - min_z).
    """

    def __init__(self) -> None:
        super().__init__()
    
    class Test(unittest.TestCase):
        def __init__(self, methodName: str, gcode_section: list[str]) -> None:
            super().__init__(methodName)
            self.gcode_section = gcode_section

        def test_move_up_z(self):
            flag1 = "move_up_z comment was not added"
            flag2 = "Z value is incorrect"
            for line in self.gcode_section:
                if ";Added in move_up_z.py" in line:
                    flag1 = "move_up_z comment was added"
                    z_index = line.index("Z")+1
                    z_num = round(float(line[z_index:z_index+4]), 2)
                    prev_z_index = line.index("was")+4
                    prev_z_num = float(line[prev_z_index:prev_z_index+4])
                    diff_index = line.index("is")+3
                    diff_num = float(line[diff_index:diff_index+4])
                    if z_num == round((prev_z_num+diff_num), 2):
                        flag2 = "Z value is correct"
            
            self.assertEqual(flag1, "move_up_z comment was added")
            self.assertEqual(flag2, "Z value is correct")

    def process(self, gcode_section: list[str]) -> list[str]:
        self.gcode_section = gcode_section
        tests = [self.Test("test_move_up_z", gcode_section)]
        return unittest.TestSuite(tests=tests)

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION