from .test_base.test_base import TestCommandProcessorInterface,  \
    TestSectionProcessorInterface, GCodeSection
from typing import List, Tuple


class ArcGcodeTestPipeline(object):
    def __init__(self, section_tests: List[TestSectionProcessorInterface],
                  command_tests: List[TestCommandProcessorInterface]) -> None:
        self.section_tests = section_tests
        self.command_tests = command_tests
        
        # Divide section test processors into the respective buckets
        self.top_metadata_tests: List[TestSectionProcessorInterface] = []
        self.startup_script_tests: List[TestSectionProcessorInterface] = []
        self.gcode_movements_tests: List[TestSectionProcessorInterface] = []
        self.end_script_tests: List[TestSectionProcessorInterface] = []
        self.bottom_comment_tests: List[TestSectionProcessorInterface] = []    

        for processor in self.section_tests:
            self.append_processors(processor)

    def append_processors(self, processor: TestSectionProcessorInterface):
        if processor.section_type() is GCodeSection.TOP_COMMENT_SECTION:
            self.top_metadata_tests.append(processor)
        elif processor.section_type() is GCodeSection.STARTUP_SCRIPT_SECTION:
            self.startup_script_tests.append(processor)
        elif processor.section_type() is GCodeSection.GCODE_MOVEMENTS_SECTION:
            self.gcode_movements_tests.append(processor)
        elif processor.section_type() is GCodeSection.END_SCRIPT_SECTION:
            self.end_script_tests.append(processor)
        elif processor.section_type() is GCodeSection.BOTTOM_COMMENT:
            self.bottom_comment_tests.append(processor)
        else:
            err_msg = f"processor section_type {processor.section_type()} " + \
                        "is invalid"
            raise ValueError(err_msg)

    def process(self) -> list[str]:
        pass