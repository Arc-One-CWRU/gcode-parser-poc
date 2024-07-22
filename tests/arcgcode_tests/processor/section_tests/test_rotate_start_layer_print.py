from ..test_base.test_base import TestSectionProcessorInterface, GCodeSection
from arcgcode.processor.base.cura import CURA_LAYER, CURA_OUTER_WALL
import re
from math import ceil
import numpy as np
import unittest


class TestRotateStartLayerPrint(TestSectionProcessorInterface, unittest.TestCase):
    """Tests that the post-processor rotates the start layer by the specified amount.
    """

    def __init__(self) -> None:
        super().__init__()
    
    class Test(unittest.TestCase):
        def __init__(self, methodName: str, gcode_section: list[str]) -> None:
            super().__init__(methodName)
            self.gcode_section = gcode_section

        def test_rotate_start_layer_print(self):
            ""

    def process(self, gcode_section: list[str]) -> list[str]:
        self.gcode_section = gcode_section
        tests = [self.Test("test_rotate_start_layer_print", gcode_section)]
        return unittest.TestSuite(tests=tests)

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION