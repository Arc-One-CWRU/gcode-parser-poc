from arcgcode.cura.settings import CuraMicerSettings
from arcgcode.pipeline import CuraGCodePipeline
from arcgcode.processor import ExtruderRemover, RotateStartLayerPrint, \
    AllWelderControl, MoveUpZ, AddMicerSettings, AddSleep, AddGcodeVersion, \
    WaitForTemp, ChangeInitialZ, ChangeMovementRate, \
    CommandProcessorInterface, SectionProcessorInterface, AddPause, ChangeG0ToG1, SpeedCapAdder


class CuraPostProcessor():
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
        section_processors: list[SectionProcessorInterface] = [
                RotateStartLayerPrint(self.settings.rotate_amount),
                AllWelderControl(),
                MoveUpZ(self.settings.weld_gap),
                AddMicerSettings(settings=self.settings),
                AddGcodeVersion(),
                ChangeInitialZ(),
                ChangeG0ToG1()
            ]
        command_processors: list[CommandProcessorInterface] = [
            ExtruderRemover(),
            SpeedCapAdder()

        ]

        if self.settings.overwrite_movement_rate:
            processor = ChangeMovementRate(self.settings.movement_rate)
            command_processors.append(processor)

        if self.settings.use_temperature_sensor:
            processor = WaitForTemp()
            section_processors.append(processor)
        else:
            section_processors.append(AddSleep(sleep_time=self.settings.sleep_time))

        if self.settings.pause_after_layer:
            processor = AddPause()
            section_processors.append(processor)

        gcode_pipeline = CuraGCodePipeline(
            section_processors=section_processors,
            command_processor=command_processors)

        new_gcode = gcode_pipeline.process(data)
        return new_gcode
