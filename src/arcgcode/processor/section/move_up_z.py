from ..base import SectionProcessorInterface, GCodeSection


class MoveUpZ(SectionProcessorInterface):
    """Translates all commands with Z arguments up by the (weld_gap - min_z).
    """

    def __init__(self, weld_gap: float) -> None:
        super().__init__()
        self.weld_gap = weld_gap

    def should_skip(self, instruction: str) -> bool:
        """Checks if the instruction should skipped.
        """
        # TODO: better regex?
        return " Z" not in instruction

    def get_z_num_from_instruction(self, instruction: str) -> float:
        z_index = instruction.index("Z") + 1
        raw_z_num = instruction[z_index:len(instruction)]
        z_num = float(raw_z_num.replace(" ", "").replace("\n", ""))
        return z_num

    def get_min_z(self, gcode_section: str) -> float:
        """
        """
        min_z = float("inf")
        instructions = gcode_section.splitlines(True)
        for instruction in instructions:
            if self.should_skip(instruction):
                continue

            z_num = self.get_z_num_from_instruction(instruction)
            min_z = min(min_z, z_num)

        return min_z

    def process(self, gcode_section: str) -> str:
        """Reads the G-Code file buffer and does an action. It should return
        the desired G-Code string for that section.
        """
        min_z = self.get_min_z(gcode_section)
        diff = self.weld_gap - min_z
        new_gcode_section = ""
        instructions = gcode_section.splitlines(True)
        for instruction in instructions:
            if self.should_skip(instruction):
                new_gcode_section += instruction
                continue

            z_index = instruction.index("Z") + 1
            z_num = diff + self.get_z_num_from_instruction(instruction)
            z_front: str = instruction[0:z_index]
            new_z_instruction = z_front + str(z_num) + "\n"
            new_gcode_section += new_z_instruction

        return new_gcode_section

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION
