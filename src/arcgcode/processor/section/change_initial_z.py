from ..base import SectionProcessorInterface, GCodeSection, version


class ChangeInitialZ(SectionProcessorInterface):
    """Changes the initial z so that the welder doesn't run into clamps and previous prints
    """

    def __init__(self) -> None:
        super().__init__()

    def process(self, gcode_section: list[str]) -> list[str]:
        """Changes the initial z so that the welder doesn't run into clamps and previous prints
        """
        new_gcode_section = []
        index = 0
        for i,line in enumerate(gcode_section):
            if line.startswith(";TYPE"):
                index = i
                break
            if line.startswith("G0"):
                if ("X" in line or "Y" in line) and "Z" in line:
                    zindex = line.find("Z")
                    new_gcode_section.append(line[0:zindex])
                elif "Z" in line:
                    new_gcode_section.append("G0 F9000 Z100")               
            else:
                new_gcode_section.append(line)
        for i,line in enumerate(new_gcode_section):
            gcode_section[i] = line
        return gcode_section

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.TOP_COMMENT_SECTION
