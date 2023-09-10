from math import modf, ceil
from enum import Enum
import re
import numpy

from dataclasses import dataclass, fields


@dataclass
class CuraMicerSettings:
    """Cura Micer Settings"""
    weld_gap: float
    sleep_time: float
    rotate_amount: float


# Maybe subclass for stuff to be remove versus total
class GCodes(Enum):
    TOOL = "T0"
    SET_EXTRUDER_TEMP = "M104"
    SET_EXTRUDER_TEMP_AND_WAIT = "M109"
    SET_EXTRUDER_TO_RELAITVE = "M83"
    SET_EXTRUDER_TO_ABOSULTE = "M82"
    FAN_OFF = "M107"
    WELD_OFF = "M42 P1 S0 ;Disable Welder\n"
    WELD_ON = "M42 P1 S1 ;Enable Welder\n"
    SLEEP = "G4"


class CuraMicer():
    """Arc One's Cura post-processing pipeline.
    """
    def __init__(self, settings: CuraMicerSettings) -> None:
        self.settings = settings

    def gcode_in_line(self, line: str) -> bool:
        for code in GCodes:
            # Non removed subclass?
            if code.value == GCodes.WELD_OFF.value:
                continue
            if line.startswith(code.value):
                return True

        return False

    def remove_extruder(self, lines: list[str]) -> list[str]:
        data2: list[str] = []
        for line in lines:
            if self.gcode_in_line(line):
                continue

            # TODO regex magic?
            if ("X" not in line and "Y" not in line and
               "Z" not in line and " E" in line):
                continue

            data2.append(line)

        return data2

    def all_welder_control(self, lines: list[str]) -> list[str]:
        data2: list[str] = []
        seen_e = False

        for i in range(len(lines)):
            line = lines[i]

            # Edge Cases
            if i - 1 < 0:
                data2.append(line)
                continue
            if i + 1 == len(lines):
                data2.append(line)
                continue

            if " E" in line and not seen_e:
                seen_e = True
                data2.append(GCodes.WELD_ON.value)
                e_index = line.find("E")
                short_line = line[e_index:len(line)]
                nums_in_line = re.findall(r"[-+]?(?:\d*\.*\d+)", short_line)
                e_value = nums_in_line[0]
                data2.append(line.replace(f"E{e_value}", ""))

            elif " E" in line and seen_e:
                e_index = line.find("E")
                short_line = line[e_index:len(line)]
                nums_in_line = re.findall(r"[-+]?(?:\d*\.*\d+)", short_line)
                e_value = nums_in_line[0]
                data2.append(line.replace(f"E{e_value}", ""))

            elif " E" not in line and seen_e:
                seen_e = False
                data2.append(GCodes.WELD_OFF.value)
                data2.append(line)
            elif " E" not in line and not seen_e:
                data2.append(line)

        return data2

    def move_up_z(self, lines: list[str], weld_gap: float) -> list[str]:
        min_z = float("inf")

        for line in lines:
            if " Z" in line:

                z_index = line.index("Z") + 1
                z_num = float(line[z_index:len(line)].replace(" ", "")
                              .replace("\n", ""))

                min_z = min(min_z, z_num)

        diff = weld_gap - min_z

        # Could store indices to skip loop through data
        data2: list[str] = []
        for line in lines:
            if " Z" in line:

                z_index = line.index("Z") + 1

                z_front: str = line[0:z_index]
                z_num = float(line[z_index:len(line)].replace(" ", "")
                              .replace("\n", ""))

                z_num += diff
                data2.append(z_front + str(z_num) + "\n")
            else:
                data2.append(line)

        return data2

    # TODO? Starting stuff gets moved but only some
    def splitter(self, data: list[str]) -> list[str]:
        """Splits the incoming data from Cura into a list
        with each element being a GCode"""
        lines2: list[str] = []
        for chunk in data:
            lines = chunk.split("\n")
            for line in lines:
                lines2.append(f'{line}\n')

        return lines2

    # Work but could use some cleaner code
    def add_sleep(self, lines: list[str], sleep_time: float) -> list[str]:
        sum_sleep_time = 0.0
        end_time = -1

        (ds, s) = modf(sleep_time)
        # Converts into ms
        ms = int(ds*1000)

        lines2: list[str] = []
        skip_first = True
        for line in lines:

            # TODO weird gap between ;LAYER and ;LAYER_COUNT
            if line.startswith(";LAYER:"):
                sum_sleep_time += sleep_time
                lines2.append(line)

                if skip_first:
                    skip_first = False
                    continue
                lines2.append(f"{GCodes.SLEEP.value} S{int(s)} P{ms}\n")

            elif line.startswith(";TIME_ELAPSED:"):
                time_elapsed = float(line[14:len(line)].replace("\n", ""))
                new_time_elapsed = time_elapsed+sum_sleep_time
                end_time = new_time_elapsed
                lines2.append(f";TIME_ELAPSED:{new_time_elapsed}")
            else:
                lines2.append(line)

        lines3: list[str] = []
        for line in lines2:
            if line.startswith(";TIME:"):
                lines3.append(f";TIME:{end_time}\n")
            else:
                lines3.append(line)

        return lines3

    def add_micer_settings(self, lines: list[str]) -> list[str]:
        lines2: list[str] = []
        for line in lines:
            GENERATED_STRING = ";Generated with Cura_SteamEngine 5.4.0"
            if line.startswith(GENERATED_STRING):
                lines2.append(f"{GENERATED_STRING} + Micer\n")

            elif line.startswith(";MAXZ:"):
                lines2.append(line)
                lines2.append("\n;Micer Settings\n")
                # Iterate over the attributes of the dataclass
                for field in fields(self.settings):
                    settings_attr = field.name
                    settings_val = getattr(self.settings, settings_attr)
                    lines2.append(f';{settings_attr} = {settings_val}\n')

            else:
                lines2.append(line)
        return lines2

    def rotate_start_layer_print(self, lines: list[str],
                                 rotate_amount: float) -> list[str]:
        lines2: list[str] = []

        wall_lines: list[str] = []
        speed = -1
        layer_count = -1
        start_wall = False
        line_count = 0
        gotten_speed = False

        for line in lines:
            if line.startswith(";LAYER:"):
                lines2.append(line)
                layer_count += 1
            elif line.startswith(";TYPE:WALL-OUTER"):
                start_wall = True
                line_count = 0
                wall_lines = []
                gotten_speed = False
                lines2.append(line)
            elif " E" not in line and start_wall:
                first_wall_line = True
                start_wall = False
                # Splits and rotate chunks
                top_num = layer_count % rotate_amount
                percentage = top_num / rotate_amount

                lines_moved = ceil(percentage*line_count)

                rotated_lines = numpy.roll(wall_lines, lines_moved)
                for wall_line in rotated_lines:
                    moved_comment = f" ;Moved {lines_moved} lines\n"
                    no_new_line = str(wall_line).replace("\n", "")

                    if first_wall_line:
                        first_line = no_new_line.replace(" ", f" F{speed} ", 1)
                        first_wall_line = False
                        lines2.append(first_line + moved_comment)
                        continue

                    lines2.append(no_new_line + moved_comment)

                lines2.append(line)
            elif start_wall:
                line_count += 1

                if line.startswith("G1 F") and not gotten_speed:
                    gotten_speed = True
                    # Gets Speed value out of a line
                    speed = re.findall(r"[-+]?(?:\d*\.*\d+)", line)[1]
                    generic_line = line.replace(f"F{speed} ", "")
                    wall_lines.append(generic_line)
                    continue

                wall_lines.append(line)
            else:
                lines2.append(line)

        return lines2

    def execute(self, data: list[str]) -> list[str]:
        """ data is 4 + layer count elements long
            data[0] is the information about the print
            data[1] Start Commands
            data[2] -> data[n-3] each layer
            data[n-2] retracts extruder
            data[n-1] End Commands
        """
        # TODO unit test to make sure order does not matter.
        lines = self.splitter(data)
        sleep = self.add_sleep(lines, self.settings.sleep_time)
        no_extruder = self.remove_extruder(sleep)
        rotate_amount = self.settings.rotate_amount
        rotated_layers = self.rotate_start_layer_print(no_extruder,
                                                       rotate_amount)
        welder = self.all_welder_control(rotated_layers)
        up_z = self.move_up_z(welder, self.settings.weld_gap)
        settings = self.add_micer_settings(up_z)
        return settings
