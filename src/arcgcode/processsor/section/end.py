from arcgcode.processsor.base.sections import GCodeSection
from ..base.base import SectionProcessorInterface


class ArcOneEndScript(SectionProcessorInterface):
    """Replaces the Cura end script with our own.
    """

    def process(self, _: str) -> str:
        """Replaces the Cura end script with our own.
        """
        end_script = """M42 P1 S0; Turn off the welder
G0 F20000 Z60; Raises the welding tip, quickly (F sets speed)
"""
        return end_script

    def section_type(self) -> GCodeSection:
        return GCodeSection.END_SCRIPT_SECTION
