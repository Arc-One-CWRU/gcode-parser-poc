import unittest
from arcgcode.v1.micer import CuraMicer
from arcgcode.v1.micer import CuraMicerSettings

class TestCuraMicer(unittest.TestCase):
    def test_gcode_in_line(self):
        settings = CuraMicerSettings(weld_gap=6, sleep_time=2, rotate_amount= 3) 
        micer = CuraMicer(settings)
        lines = ["T0", "M104", "M109", "M83", "M82", "M107", "M42 P1 S1 ;Enable Welder\n", "G4"]
        for line in lines:
            self.assertTrue(micer.gcode_in_line(line))
        
        line = "M42 P1 S0 ;Disable Welder\n"
        self.assertFalse(micer.gcode_in_line(line))
        line = "bob"
        self.assertFalse(micer.gcode_in_line(line))

    def test_remove_extruder(self):
        settings = CuraMicerSettings(weld_gap=6, sleep_time=2, rotate_amount= 3) 
        micer = CuraMicer(settings)
        lines = ["M104", "G24 X82", "G29 Y74", "G33 Z42", "G22 E6", "G2 X24 Y330 Z42", "M42 P1 S0 ;Disable Welder\nE"]
        lines2 = ["G24 X82", "G29 Y74", "G33 Z42", "G2 X24 Y330 Z42", "M42 P1 S0 ;Disable Welder\nE"]
        self.assertEqual(lines2, micer.remove_extruder(lines))

    def test_all_welder_control(self):
        settings = CuraMicerSettings(weld_gap=6, sleep_time=2, rotate_amount= 3) 
        micer = CuraMicer(settings)
        lines = ["M104", "G24 E82", "G29 E74", "G33 Z42", "G2 X24 Y330 Z42", "G89 Z42"]
        lines2 = ["M104", "M42 P1 S1 ;Enable Welder\n", "G24 ", "G29 ", "M42 P1 S0 ;Disable Welder\n", "G33 Z42", "G2 X24 Y330 Z42", "G89 Z42"]
        self.assertEqual(lines2, micer.all_welder_control(lines))

    def test_move_up_z(self):
        settings = CuraMicerSettings(weld_gap=6, sleep_time=2, rotate_amount= 3) 
        micer = CuraMicer(settings)
        lines = ["M104", "G24 Z82", "G29 Z74", "G33 Z42", "G2 X24 Y330 Z2", "G89 Z42"]
        lines2 = ["M104", "G24 Z86.0\n", "G29 Z78.0\n", "G33 Z46.0\n", "G2 X24 Y330 Z6.0\n", "G89 Z46.0\n"]
        self.assertEqual(lines2, micer.move_up_z(lines,6))
    
    def test_splitter(self):
        settings = CuraMicerSettings(weld_gap=6, sleep_time=2, rotate_amount= 3) 
        micer = CuraMicer(settings)
        lines = ["M107", "M42 P1 S1 ;Enable Welder\nM42 P1 S0 ;Disable Welder", "G4"]
        lines2 = ["M107\n", "M42 P1 S1 ;Enable Welder\n", "M42 P1 S0 ;Disable Welder\n", "G4\n"]
        self.assertEqual(lines2, micer.splitter(lines))
    
    def test_add_sleep(self):
        settings = CuraMicerSettings(weld_gap=6, sleep_time=2.2, rotate_amount= 3) 
        micer = CuraMicer(settings)
        lines = [";LAYER: 1", ";LAYER: 2", ";TIME_ELAPSED: 42", "M102"]
        lines2 = [";LAYER: 1", ";LAYER: 2", "G4 S2 P200\n", ";TIME_ELAPSED:46.4", "M102"]
        self.assertEqual(lines2, micer.add_sleep(lines, 2.2))

    def add_micer_settings(self):
        settings = CuraMicerSettings(weld_gap=6, sleep_time=2, rotate_amount= 3) 
        micer = CuraMicer(settings)
        lines = [";Generated with Cura_SteamEngine 5.4.0", ";MAXZ: 42", "M104"]
        lines2 = [";Generated with Cura_SteamEngine 5.4.0 + Micer\n", ";MAXZ: 42", "\nMicer Settings\n", "M104"]
        self.assertEqual(lines2, micer.add_micer_settings(lines))

    
    
    

if __name__ == "__main__":
    unittest.main()