import unittest
from arcgcode.processor import ExtruderRemover, RotateStartLayerPrint, \
    AllWelderControl, MoveUpZ, AddMicerSettings, AddSleep
from arcgcode.pipeline import CuraGCodePipeline
from arcgcode.v1.micer import CuraMicerSettings


def new_pipeline(settings: CuraMicerSettings) -> CuraGCodePipeline:
    gcode_pipeline = CuraGCodePipeline(
        section_processors=[
            AddSleep(sleep_time=settings.sleep_time),
            RotateStartLayerPrint(settings.rotate_amount),
            AllWelderControl(), MoveUpZ(settings.weld_gap),
            AddMicerSettings(settings=settings),
        ],
        command_processor=[ExtruderRemover()])
    return gcode_pipeline


def new_blank_pipeline(settings: CuraMicerSettings) -> CuraGCodePipeline:
    gcode_pipeline = CuraGCodePipeline(
        section_processors=[],
        command_processor=[],
    )
    return gcode_pipeline


def read_cube_lightning_gcode_file() -> list[str]:
    with open("./gcodes/inputs/cube_lightning.gcode") as f:
        data = f.readlines()
    return data


def read_line_gcode_file() -> list[str]:
    with open("./gcodes/inputs/CFFFP_WeldingLineTestJoseph.gcode") as f:
        data = f.readlines()
    return data


class TestCuraGCodePipeline(unittest.TestCase):
    def test_read_top_metadata(self):
        settings = CuraMicerSettings(weld_gap=6, sleep_time=2, rotate_amount=3)
        pipeline = new_pipeline(settings)
        input_gcode = read_cube_lightning_gcode_file()
        top_metadata, end_idx = pipeline.read_top_metadata(input_gcode, 0)
        self.assertNotEqual(top_metadata, "")
        self.assertGreater(end_idx, 0)
        self.assertEqual(input_gcode[end_idx],
                         ";Generated with Cura_SteamEngine 5.3.1\n")

    def test_read_startup_script(self):
        settings = CuraMicerSettings(weld_gap=6, sleep_time=2, rotate_amount=3)
        pipeline = new_pipeline(settings)
        input_gcode = read_cube_lightning_gcode_file()
        _, meta_end_idx = pipeline.read_top_metadata(input_gcode, 0)
        startup_script, end_idx = pipeline.read_startup_script(input_gcode,
                                                               meta_end_idx+1)
        self.assertNotEqual(startup_script, "")
        self.assertGreater(end_idx, 0)
        self.assertEqual(input_gcode[end_idx],
                         ";LAYER_COUNT:132\n")
        
    def test_full_pipeline_example(self):
        settings = CuraMicerSettings(weld_gap=6, sleep_time=2, rotate_amount=3)
        pipeline = new_blank_pipeline(settings)
        input_gcode = read_line_gcode_file()
        new_gcode_file = pipeline.process(input_gcode)
        print(new_gcode_file)


if __name__ == "__main__":
    unittest.main()
