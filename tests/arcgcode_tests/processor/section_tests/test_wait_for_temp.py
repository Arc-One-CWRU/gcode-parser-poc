from ..test_base.test_base import TestSectionProcessorInterface, GCodeSection
import unittest


class TestWaitForTemp(TestSectionProcessorInterface, unittest.TestCase):
    """Tests that post-processor added command to wait for designated 
       temperature after each layer before continuing.
    """

    def __init__(self) -> None:
        super().__init__()
    
    class Test(unittest.TestCase):
        def __init__(self, methodName: str, gcode_section: list[str]) -> None:
            super().__init__(methodName)
            self.gcode_section = gcode_section

        def test_wait_for_temp(self):
            if ";Added in wait_for_temp.py" in self.gcode_section:
                line = 1
                while line < len(self.gcode_section):
                    if self.gcode_section[line].startswith(";LAYER:") and "0" not in self.gcode_section[line][7]:
                        self.assertEqual(
                            self.gcode_section[line+1:line+12],
                            ['G91 ;Added in wait_for_temp.py\n',
                            'G1 Z40 ;Added in wait_for_temp.py\n',
                            'G1 X72 Y74 ;Added in wait_for_temp.py\n',
                            'G4 P0 ;Added in wait_for_temp.py\n',
                            'M291 P"Interpass Start" ;Added in wait_for_temp.py\n',
                            'M98 P"/macros/WaitForInterpassTemp.g" ;Added in wait_for_temp.py\n',
                            'G4 P0 ;Added in wait_for_temp.py\n',
                            'M291 P"Interpass End" ;Added in wait_for_temp.py\n',
                            'G1 X-72 Y-74 ;Added in wait_for_temp.py\n',
                            'G1 Z-40 ;Added in wait_for_temp.py\n',
                            'G90 ;Added in wait_for_temp.py\n'])
                    line += 1

    def process(self, gcode_section: list[str]) -> list[str]:
        self.gcode_section = gcode_section
        tests = [self.Test("test_wait_for_temp", gcode_section)]
        return unittest.TestSuite(tests=tests)

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION