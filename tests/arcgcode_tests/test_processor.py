from arcgcode.cura.settings import CuraMicerSettings
from .test_pipeline import ArcGcodeTestPipeline
from .processor import TestCommandProcessorInterface,  \
    TestSectionProcessorInterface, TestAddGcodeVersion,  \
    TestAddMicerSettings, TestAddSleep, TestChangeG0ToG1,  \
    TestChangeInitialZ, TestMoveUpZ, TestPostHome,  \
    TestRotateStartLayerPrint, TestWaitForTemp


class ArcGcodeTestProcessor():
    def __init__(self, settings: CuraMicerSettings) -> None:
        self.settings = settings

    def execute(self, data) -> list[str]:
        section_tests_processors: list[TestSectionProcessorInterface] = [
            TestAddGcodeVersion(),
            TestAddMicerSettings(settings=self.settings),
            TestMoveUpZ(),
            TestRotateStartLayerPrint(),
        ]

        command_tests_processors: list[TestCommandProcessorInterface] = [
        ]

        if self.settings.change_initial_Z:
            processor = TestChangeInitialZ()
            section_tests_processors.append(processor)

        if self.settings.change_G0toG1:
            processor = TestChangeG0ToG1()
            section_tests_processors.append(processor)

        # if self.settings.overwrite_movement_rate:
        #     processor = TestChangeMovementRate(self.settings.movement_rate)
        #     command_tests_processors.append(processor)

        # if self.settings.pause_after_layer:
        #     processor = TestAddPause()
        #     section_tests_processors.append(processor)

        if self.settings.use_temperature_sensor:
            processor = TestWaitForTemp()
            section_tests_processors.append(processor)
        else:
            section_tests_processors.append(TestAddSleep(sleep_time=self.settings.sleep_time))

        if self.settings.return_home:
            processor = TestPostHome()
            section_tests_processors.append(processor)

        test_pipeline = ArcGcodeTestPipeline(
            section_tests_processors, 
            command_tests_processors)

        test_pipeline.process(data)
