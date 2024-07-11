from .test_base.test_base import TestCommandProcessorInterface,  \
    TestSectionProcessorInterface, GCodeSection
from typing import List, Tuple
import unittest
from arcgcode.pipeline import CuraGCodePipeline


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

    def process(self, data) -> list[str]:
        """Collects all of the tests and combines them into a single test
        suite."""

        # Top Comment Section Tests
        top_metadata, top_metadata_end_index = CuraGCodePipeline.read_top_metadata(data,0)
        top_metadata_tests = []
        for test in self.top_metadata_tests:
            top_metadata_tests.append(test.process(top_metadata))
        top_metadata_test_suite = unittest.TestSuite(tests=top_metadata_tests)

        # Startup Script Section Tests
        startup_script, startup_script_end_index = CuraGCodePipeline.read_startup_script(data,top_metadata_end_index+1)
        startup_script_tests = []
        for test in self.startup_script_tests:
            startup_script_tests.append(test.process(startup_script))
        startup_script_test_suite = unittest.TestSuite(tests=startup_script_tests)

        # GCode Movements Section Tests
        gcode_movements, gcode_movements_end_index = CuraGCodePipeline.read_gcode_movements(data,startup_script_end_index+1)
        gcode_movements_tests = []
        for test in self.gcode_movements_tests:
            gcode_movements_tests.append(test.process(gcode_movements))
        gcode_movements_test_suite = unittest.TestSuite(tests=gcode_movements_tests)

        # End Script Section Tests
        end_script, end_script_end_index = CuraGCodePipeline.read_end_script(data,gcode_movements_end_index+1)
        end_script_tests = []
        for test in self.end_script_tests:
            end_script_tests.append(test.process(end_script))
        end_script_test_suite = unittest.TestSuite(tests=end_script_tests)

        # Bottom Comment Section Tests
        bottom_comment, bottom_comment_end_index = CuraGCodePipeline.read_bottom_comment(data,end_script_end_index+1)
        bottom_comment_tests = []
        for test in self.bottom_comment_tests:
            bottom_comment_tests.append(test.process(bottom_comment))
        bottom_comment_test_suite = unittest.TestSuite(tests=bottom_comment_tests)

        final_suite = unittest.TestSuite([top_metadata_test_suite,
                                          startup_script_test_suite,
                                          gcode_movements_test_suite,
                                          end_script_test_suite,
                                          bottom_comment_test_suite])
        test_runner = unittest.TextTestRunner(verbosity=2)
        test_runner.run(final_suite)

