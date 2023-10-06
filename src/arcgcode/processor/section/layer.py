import re
from typing import List
from ..base import SectionProcessorInterface, GCodeSection, CURA_LAYER


class ExcludeCuraLayer(SectionProcessorInterface):
    """Exclude layer (;LAYER:) processor from a Cura Engine G-Code based on the
    provided layers indices.
    """

    def __init__(self, ignore_layer_indices: List[int]) -> None:
        super().__init__()
        self.is_start_of_layer_matcher = re.compile(r';[A-Z]')
        self.ignore_layer_indices = ignore_layer_indices

    def process(self, gcode_section: list[str]) -> list[str]:
        """Reads the gcode section line by line and excludes the specified
        layers.
        """
        should_exclude = False
        new_gcode_section: list[str] = []
        for instruction in gcode_section:
            if instruction.startswith(CURA_LAYER):
                # Parse layer idx so we can check if we need to exclude
                # this layer.
                #
                # Must strip the string because there are be leading/trailing
                # whitespace that makes layer_idx.isdigit() false
                # I.e. ;LAYER:0 -> layer_idx = 0
                layer_idx = instruction.split(":")[1].strip()
                if layer_idx.isdigit():
                    try:
                        should_exclude = int(
                            layer_idx) in self.ignore_layer_indices
                    except ValueError:
                        continue
            elif self.is_start_of_layer_matcher.match(instruction):
                # Reset upon discovering new layer
                should_exclude = False

            # Only include correct layer instructions
            if not should_exclude:
                new_gcode_section.append(instruction)
        return new_gcode_section

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION
