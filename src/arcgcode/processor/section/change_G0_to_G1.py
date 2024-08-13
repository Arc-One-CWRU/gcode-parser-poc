from ..base import SectionProcessorInterface, GCodeSection


class ChangeG0ToG1(SectionProcessorInterface):
    """Changes G0 to G1
    """

    def __init__(self) -> None:
        super().__init__()

    def process(self, gcode_section: list[str]) -> list[str]:
        """Reads the G-Code file buffer and does an action. It should return
        the desired G-Code string for that section.
        """
        # Sanity check, just in case there's an extra new line at the end of
        # the section for some reas

        new_gcode_section: list[str] = []

        for line in gcode_section:
            if line.startswith("G0"):
                new_gcode_section.append(f"G1{line[2:].strip()} ;Changed in change_G0_to_G1.py")
            else:
                new_gcode_section.append(line)
        return new_gcode_section
       
    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION
