import unittest
from arcgcode.processor.section import RotateStartLayerPrint


def read_cube_movements_section() -> list[str]:
    with open("./gcodes/inputs/cube_movements.gcode") as f:
        data = f.readlines()
    return data


class TestCuraRotateStartLayerPrint(unittest.TestCase):
    def test_process(self):
        cube_movements = read_cube_movements_section()
        processor = RotateStartLayerPrint(6)
        processed_movements = processor.process(cube_movements)
        self.assertEqual(len(processed_movements), 9897)


if __name__ == "__main__":
    unittest.main()
