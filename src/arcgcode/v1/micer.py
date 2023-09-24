import io
from arcgcode.cura.settings import CuraMicerSettings
from arcgcode.pipeline import CuraGCodePipeline
from arcgcode.processor import ExtruderRemover, RotateStartLayerPrint, \
    AllWelderControl, MoveUpZ, AddMicerSettings, AddSleep


class CuraMicer():
    """Arc One's Cura post-processing pipeline.
    """
    def __init__(self, settings: CuraMicerSettings) -> None:
        self.settings = settings

    def execute(self, data: list[str]) -> list[str]:
        """ data is 4 + layer count elements long
            data[0] is the information about the print
            data[1] Start Commands
            data[2] -> data[n-3] each layer
            data[n-2] retracts extruder
            data[n-1] End Commands
        """
        gcode_pipeline = CuraGCodePipeline(
            section_processors=[
                AddSleep(sleep_time=self.settings.sleep_time),
                RotateStartLayerPrint(self.settings.rotate_amount),
                AllWelderControl(), MoveUpZ(self.settings.weld_gap),
                AddMicerSettings(settings=self.settings),
            ],
            command_processor=[ExtruderRemover()])
        new_gcode = gcode_pipeline.process(io.StringIO("".join(data)))
        return new_gcode.splitlines(keepends=True)
