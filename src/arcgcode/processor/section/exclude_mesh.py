import re
from ..base import SectionProcessorInterface, GCodeSection, CURA_MESH_LAYER


class ExcludeMeshLayer(SectionProcessorInterface):
    """The 'mesh' layer is not really a layer. It's more of a pre-layer script.
    This processor excludes all mesh layers from a G-Code.
    """

    def __init__(self) -> None:
        super().__init__()
        self.is_start_of_layer_matcher = re.compile(r';[A-Z]')

    def process(self, gcode_section: list[str]) -> list[str]:
        """Reads the G-Code file buffer and does an action. It should return
        the desired G-Code string for that section.
        """
        is_mesh_layer = False
        new_gcode_section: list[str] = []
        for instruction in gcode_section:
            if instruction.startswith(CURA_MESH_LAYER):
                is_mesh_layer = True
            elif self.is_start_of_layer_matcher.match(instruction):
                # Reset upon discovering new layer
                is_mesh_layer = False

            # Only include non-mesh layer instructions
            if not is_mesh_layer:
                new_gcode_section.append(instruction) 
            else:
                new_gcode_section.append(f";{instruction} ;Removed in exclude_mesh.py")
        return new_gcode_section

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION
