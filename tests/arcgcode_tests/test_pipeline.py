from .processor import TestCommandProcessorInterface,  \
    TestSectionProcessorInterface, GCodeSection
from typing import List, Tuple
import unittest
from arcgcode.pipeline import CuraGCodePipeline
from arcgcode.processor.base.cura import END_OF_TOP_METADATA, END_OF_STARTUP_SCRIPT, \
    END_OF_GCODE, find_end_of_gcode_movements_idx


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

    def read_section(self, gcode_data: list[str],
                     start_idx: int,
                     end_indicator: str) -> Tuple[list[str], int]:
        """Generic utility function for reading a section.

        Args:
            gcode_data: a list of the gcode commands. Each command should end
            with a new line.
            start_idx: the start of the section to process
            end_indicator: the start of a line that indicates the end of the
            section to process

        Returns:
            str: the section
            int: the index of the last element of the section processed
        """
        is_in_section = True
        section_contents: list[str] = []
        iter_idx = start_idx
        while is_in_section and iter_idx < len(gcode_data):
            curr_line = gcode_data[iter_idx]
            section_contents.append(curr_line)
            if curr_line.strip().startswith(end_indicator):
                is_in_section = False
            iter_idx += 1

        return section_contents, iter_idx-1

    def read_top_metadata(self, gcode_data: list[str],
                          start_idx: int) -> Tuple[list[str], int]:
        """Reads the top metadata comments.

        Returns the top metadata and the last index of the top metadata
        inclusive.

        So if the top metadata ends at index=2, then it will return index 2.
        """
        return self.read_section(gcode_data, start_idx, END_OF_TOP_METADATA)

    def read_startup_script(self, gcode_data: list[str],
                            start_idx: int) -> Tuple[list[str], int]:
        """Reads the startup script. Assumes that the top metadata has already
        been read.

        Returns the startup script section and the last index of the section
        inclusive.
        """
        return self.read_section(gcode_data, start_idx,
                                 END_OF_STARTUP_SCRIPT)

    def read_gcode_movements(self, gcode_data: list[str],
                             start_idx: int) -> Tuple[list[str], int]:
        """Reads the actual movement G-Code instructions.

        Returns the GCode movements section and the last index of the section
        inclusive.
        """
        # Similar to read_section except that it needs to check the next line
        # since the end indicator can occur multiple times throughout the
        # G-Code
        section_contents: list[str] = []
        iter_idx = start_idx
        end_idx = find_end_of_gcode_movements_idx(gcode_data)
        while iter_idx <= end_idx:
            curr_line = gcode_data[iter_idx]
            section_contents.append(curr_line)
            iter_idx += 1

        return section_contents, iter_idx-1

    def read_end_script(self, gcode_data: list[str],
                        start_idx: int) -> Tuple[list[str], int]:
        """Reads the end script.
        """
        return self.read_section(gcode_data, start_idx, END_OF_GCODE)

    def read_bottom_comment(self, gcode_data: list[str],
                            start_idx: int) -> Tuple[list[str], int]:
        """Reads the bottom comment. Can do so by reading the rest of the
        buffer.
        """
        return gcode_data[start_idx:], len(gcode_data) - 1

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
        top_metadata, top_metadata_end_index = self.read_top_metadata(data, 0)
        top_metadata_tests = []
        for test in self.top_metadata_tests:
            top_metadata_tests.append(test.process(top_metadata))
        top_metadata_test_suite = unittest.TestSuite(tests=top_metadata_tests)
        print(top_metadata)

        # Startup Script Section Tests
        startup_script, startup_script_end_index = self.read_startup_script(data,top_metadata_end_index+1)
        startup_script_tests = []
        for test in self.startup_script_tests:
            startup_script_tests.append(test.process(startup_script))
        startup_script_test_suite = unittest.TestSuite(tests=startup_script_tests)
        print(startup_script)
        # GCode Movements Section Tests
        gcode_movements, gcode_movements_end_index = self.read_gcode_movements(data,startup_script_end_index+1)
        gcode_movements_tests = []
        for test in self.gcode_movements_tests:
            gcode_movements_tests.append(test.process(gcode_movements))
        gcode_movements_test_suite = unittest.TestSuite(tests=gcode_movements_tests)

        # End Script Section Tests
        end_script, end_script_end_index = self.read_end_script(data,gcode_movements_end_index+1)
        end_script_tests = []
        for test in self.end_script_tests:
            end_script_tests.append(test.process(end_script))
        end_script_test_suite = unittest.TestSuite(tests=end_script_tests)
        print(end_script)
        # Bottom Comment Section Tests
        bottom_comment, bottom_comment_end_index = self.read_bottom_comment(data,end_script_end_index+1)
        bottom_comment_tests = []
        for test in self.bottom_comment_tests:
            bottom_comment_tests.append(test.process(bottom_comment))
        bottom_comment_test_suite = unittest.TestSuite(tests=bottom_comment_tests)
        print(bottom_comment)
        final_suite = unittest.TestSuite([top_metadata_test_suite,
                                          startup_script_test_suite,
                                          gcode_movements_test_suite,
                                          end_script_test_suite,
                                          bottom_comment_test_suite])
        test_runner = unittest.TextTestRunner(verbosity=2)
        test_runner.run(final_suite)

