from ..base import SectionProcessorInterface, GCodeSection


class ChangeG0ToG1(SectionProcessorInterface):
    """Changes all G0 commands to G1 commands in the movements section
    """

    def __init__(self) -> None:
        super().__init__()

    def process(self, gcode_section: list[str]) -> list[str]:
        """Changes all G0 commands to G1 commands in the movements section
        """
        # Sanity check, just in case there's an extra new line at the end of
        # the section for some reas

        new_gcode_section: list[str] = []

        for line in gcode_section:
            if line.startswith("G0"):
                new_gcode_section.append(f"G1{line[2:]}")
            else:
                new_gcode_section.append(line)
        return new_gcode_section
       
    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION
