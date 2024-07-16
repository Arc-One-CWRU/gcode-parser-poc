from arcgcode.cura.settings import CuraMicerSettings
from .test_pipeline import ArcGcodeTestPipeline
from .processor import TestCommandProcessorInterface,  \
    TestSectionProcessorInterface, TestAddGcodeVersion, TestEnd


class ArcGcodeTestProcessor():
    def __init__(self, settings: CuraMicerSettings) -> None:
        self.settings = settings

    def execute(self, data) -> list[str]:
        section_tests_processors: list[TestSectionProcessorInterface] = [
            TestAddGcodeVersion(),
            TestAddMicerSettings(),
            TestAddPauseAfterLayer(),
            TestAddSleep(),
            TestChangeG0ToG1(),
            TestChangeInitialZ(),
            TestEnd(),
            TestExcludeMesh(),
            TestLayer(),
            TestMoveUpZ(),
            TestPostHome(),
            TestRotateStartLayerPrint(),
            TestStartup(),
            TestWaitForTemp(),
            TestWeldControl()
        ]

        command_tests_processors: list[TestCommandProcessorInterface] = [
        ]

        test_pipeline = ArcGcodeTestPipeline(
            section_tests_processors, 
            command_tests_processors)

        test_pipeline.process(data)
