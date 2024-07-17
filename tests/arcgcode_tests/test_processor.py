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
            TestAddSleep(),
            TestChangeG0ToG1(),
            TestChangeInitialZ(),
            TestMoveUpZ(),
            TestPostHome(),
            TestRotateStartLayerPrint(),
            TestWaitForTemp()
        ]

        command_tests_processors: list[TestCommandProcessorInterface] = [
        ]

        test_pipeline = ArcGcodeTestPipeline(
            section_tests_processors, 
            command_tests_processors)

        test_pipeline.process(data)
