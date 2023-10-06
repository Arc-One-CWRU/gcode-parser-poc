from abc import ABCMeta, abstractmethod
from .sections import GCodeSection


class CommandProcessorInterface:
    """Processes a matched G-Code instruction line.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def process(self, gcode_instruction: str) -> str:
        """Matches a G-Code instruction. It should return
        the desired G-Code string for that line.
        """
        raise NotImplementedError


class SectionProcessorInterface:
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
        action. It should return the desired G-Code as a list[str] for that
        section.
        """
        raise NotImplementedError

    @abstractmethod
    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        raise NotImplementedError

    # Need to think more about this.
    # def layers_to_apply(self) -> List[int]:
    #     """Gets the layers to apply the transform.
    #     """
    #     raise NotImplementedError
