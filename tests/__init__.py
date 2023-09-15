import unittest
from arcgcode.v1.micer import CuraMicer


class TestCuraMicer(unittest.TestCase):
    def test_gcode_in_line(self):
        micer = CuraMicer("")
        lines = ["T0", "M104", "M109", "M83", "M82", "M107", "M42 P1 S1 ;Enable Welder\n", "G4"]
        for line in lines:
            self.assertTrue(micer.gcode_in_line(line))
        
        line = "M42 P1 S0 ;Disable Welder\n"
        self.assertFalse(micer.gcode_in_line(line))
        line = "bob"
        self.assertFalse(micer.gcode_in_line(line))

    def test_splitter(self):
        micer = CuraMicer("")
        lines = ["M107", "M42 P1 S1 ;Enable Welder\nM42 P1 S0 ;Disable Welder", "G4"]
        lines2 = ["M107\n", "M42 P1 S1 ;Enable Welder\n", "M42 P1 S0 ;Disable Welder\n", "G4\n"]
        self.assertEqual(lines2, micer.splitter(lines))

if __name__ == "__main__":
    unittest.main()