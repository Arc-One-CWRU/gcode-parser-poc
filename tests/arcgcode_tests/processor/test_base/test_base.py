from abc import ABCMeta, abstractmethod
from arcgcode.processor.base.sections import GCodeSection
import unittest


class TestCommandProcessorInterface(unittest.TestCase):
    """Processes a matched G-Code instruction line.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def process(self, gcode_instruction: str) -> str:
        """Matches a G-Code instruction. It should return
        a boolean dependent on if the line has the expected value from running
        its matching Command Processor.
        """
        raise NotImplementedError


class TestSectionProcessorInterface(unittest.TestCase):
    """A section processor should be applied on a "section", such as:
    1. Top Comment (Settings & Metadata)
    2. Startup Script
    3. G-Code Movements
        - Pre-Layer Action
        - Movement
        - Post-Layer Action
    4. End Script
    5. Bottom Comment
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def process(self, gcode_section: list[str]) -> list[str]:
        """Reads the G-Code file with each command as an element and does an
        action. It should return a boolean dependent on if the expected
        commands are present from running its matching Section Processor.
        """
        raise NotImplementedError

    @abstractmethod
    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        raise NotImplementedError
