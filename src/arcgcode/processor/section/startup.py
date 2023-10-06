from arcgcode.processor.base.sections import GCodeSection
from ..base.base import SectionProcessorInterface


class ArcOneStartup(SectionProcessorInterface):
    """Replaces the existing startup script with our own.
    """

    def process(self, gcode_section: list[str]) -> list[str]:
        """Replaces the startup script with our own.
        """
        setup_instructions = [
            "G1 Z60 F6000; Raise the welding tip\n"
            "G0 F600 X342.474 Y120; Move to the starting spot\n",
            "G0 F6000 Z0.3; Lower the tip\n",
            "M42 P1 S1; Turn on the welder\n"
        ]

        return setup_instructions

    def section_type(self) -> GCodeSection:
        return GCodeSection.STARTUP_SCRIPT_SECTION
