from ..base import SectionProcessorInterface, GCodeSection
from math import modf
from arcgcode.cura.gcodes import GCodes
from arcgcode.processor.base.cura import CURA_LAYER, END_OF_GCODE_MOVEMENTS, \
    find_end_of_gcode_movements_idx


class AddSleep(SectionProcessorInterface):
    """Adds sleep after each layer.
    """

    def __init__(self, sleep_time: float) -> None:
        super().__init__()
        self.sleep_time = sleep_time

    def process(self, gcode_section: list[str]) -> list[str]:
        """Reads the G-Code file buffer and does an action. It should return
        the desired G-Code string for that section.
        """
        # Sanity check, just in case there's an extra new line at the end of
        # the section for some reason.
        end_of_movements_idx = find_end_of_gcode_movements_idx(gcode_section)

        new_gcode_section: list[str] = []
        sum_sleep_time = 0.0
        end_time = -1

        (ds, s) = modf(self.sleep_time)
        # Converts into ms
        ms = int(ds*1000)
        skip_first = True
        for idx, instruction in enumerate(gcode_section):
            if instruction.startswith(CURA_LAYER):
                new_gcode_section.append(instruction)
                if skip_first:
                    skip_first = False
                    continue
                sum_sleep_time += self.sleep_time
                sleep_instruction = f"{GCodes.SLEEP.value} S{int(s)} P{ms}\n"
                new_gcode_section.append(sleep_instruction + ";Added Sleep in add_sleep.py")
            # Only care about the end of the movements section.
            # Assumed that it is Cura.
            elif idx == end_of_movements_idx:
                if not instruction.startswith(END_OF_GCODE_MOVEMENTS):
                    raise Exception(f"expected {END_OF_GCODE_MOVEMENTS} as " +
                                    f"last element, but got {instruction}")

                offset = len(";TIME_ELAPSED:")
                time_elapsed = float(instruction[offset:len(instruction)].
                                     replace("\n", ""))
                new_time_elapsed = time_elapsed+sum_sleep_time
                end_time = new_time_elapsed
                new_gcode_section.append(f";TIME_ELAPSED:{new_time_elapsed}")
            else:
                new_gcode_section.append(instruction)

        section_with_time: list[str] = []
        for line in new_gcode_section:
            if line.startswith(";TIME:"):
                section_with_time.append(f";TIME:{end_time}\n")
            else:
                section_with_time.append(line)

        return section_with_time

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION
