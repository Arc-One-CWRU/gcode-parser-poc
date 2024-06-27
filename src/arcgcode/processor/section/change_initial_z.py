from ..base import SectionProcessorInterface, GCodeSection, CURA_LAYER, \
    CURA_TYPE_LAYER


class ChangeInitialZ(SectionProcessorInterface):
    """Changes the initial z so that the welder doesn't run into clamps and
    previous prints
    """

    def __init__(self) -> None:
        super().__init__()

    def process(self, gcode_section: list[str]) -> list[str]:
        """Changes the initial z so that the welder doesn't run into clamps
        and previous prints.

        Does so by adding:
        1. G0 F9000 Z100 right before the initial instruction to move to the
        print starting point.
        2. Then, adding Z100 to the initial starting point instruction prevents
        the welder from moving diagonally into clamps on its way down.
        """
        new_gcode_section: list[str] = []
        is_layer_zero = False
        INITIAL_Z_MOVE = "G0 F9000 Z100"
        for i, line in enumerate(gcode_section):
            # We only want to add the INITIAL_Z_MOVE in LAYER:0
            # This checks for a layer switch
            is_new_layer = line.startswith(CURA_LAYER) or \
                line.startswith(CURA_TYPE_LAYER)
            if is_new_layer:
                if line.startswith(CURA_LAYER):
                    layer_count = int(line.strip().split(":")[-1])
                    if layer_count == 0:
                        is_layer_zero = True
                else:
                    # The moment we encounter a non-LAYER layer, we're past the
                    # 1st layer
                    # On layer change append!
                    if is_layer_zero:
                        new_gcode_section.insert(-1, ";Initial Z Offset Changed by change_initial_z.py")  
                        new_gcode_section.insert(-1, INITIAL_Z_MOVE)
                        new_gcode_section.insert(-1, '\n')
                        
                    is_layer_zero = False

            if is_layer_zero and line.startswith("G0"):
                if ("X" in line or "Y" in line) and "Z" in line:
                    zindex = line.find("Z")
                    new_gcode_section.append("")
                    new_gcode_section.append("G1" + line[2:zindex])
            elif is_layer_zero and line.startswith(";TYPE"):
                new_gcode_section.append(new_gcode_section[len(new_gcode_section)-1])
                new_gcode_section.append(line)
            else:
                new_gcode_section.append(line)

        return new_gcode_section

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION
