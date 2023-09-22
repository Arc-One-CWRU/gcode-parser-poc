from ..base import SectionProcessorInterface, GCodeSection
from math import modf
from arcgcode.cura.gcodes import GCodes


class AddSleep(SectionProcessorInterface):
    """Adds sleep.
    """

    def __init__(self, sleep_time: float) -> None:
        super().__init__()
        self.sleep_time = sleep_time

    def process(self, gcode_section: str) -> str:
        """Reads the G-Code file buffer and does an action. It should return
        the desired G-Code string for that section.
        """
        new_gcode_section = ""
        instructions = gcode_section.splitlines(True)
        sum_sleep_time = 0.0
        end_time = -1

        (ds, s) = modf(self.sleep_time)
        # Converts into ms
        ms = int(ds*1000)

        # lines2: list[str] = []
        skip_first = True
        for instruction in instructions:
            # TODO weird gap between ;LAYER and ;LAYER_COUNT
            if instruction.startswith(";LAYER:"):
                sum_sleep_time += self.sleep_time
                new_gcode_section += instruction
                if skip_first:
                    skip_first = False
                    continue
                new_gcode_section += f"{GCodes.SLEEP.value} S{int(s)} P{ms}\n"

            elif instruction.startswith(";TIME_ELAPSED:"):
                offset = len(";TIME_ELAPSED:")
                time_elapsed = float(instruction[offset:len(instruction)].
                                     replace("\n", ""))
                new_time_elapsed = time_elapsed+sum_sleep_time
                end_time = new_time_elapsed
                new_gcode_section += f";TIME_ELAPSED:{new_time_elapsed}"
            else:
                new_gcode_section += instruction

        processed_lines = new_gcode_section.splitlines(True)
        lines3: list[str] = []
        for line in processed_lines:
            if line.startswith(";TIME:"):
                lines3.append(f";TIME:{end_time}\n")
            else:
                lines3.append(line)

        return "".join(lines3)

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION
