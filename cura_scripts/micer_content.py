# import re
from enum import Enum
from ..Script import Script
from UM.Logger import Logger
from math import modf
# Has to be place in
# C:\Program Files\UltiMaker Cura 5.4.0\share\
# cura\plugins\PostProcessingPlugin\scripts
# I made a symlink between there and the symlink_micer.py file


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


class Micer(Script):
    sum_sleep_time = 0.0
    end_time = -1
    keywords = ["weldgap", "sleeptime"]

    def getSettingDataString(self) -> str:
        # TODO make this JSON be compliant with linter
        return """{
        "name": "Micer",
        "key": "Micer",
        "metadata":{},
        "version": 2,
        "settings":{
            "weldgap": {
                "label": "Set Weld Gap",
                "description": "Set the welding gap. (mm)",
                "type": "float",
                "default_value": 8,
                "minimum_value": 0,
                "maximum_value": 1000,
                "maximum_value_warning": 100
            },
            "sleeptime": {
                "label": "Set Sleep Time",
                "description": "Set the layer sleep time. (s)",
                "type": "float",
                "default_value": 30,
                "minimum_value": 0
            }
        }
        }"""

    def remove_extruder(self, lines: list[str]) -> list[str]:
        data2: list[str] = []
        for line in lines:
            not_removed = True
            for code in GCodes:
                if line.startswith(code.value):
                    not_removed = False
                    continue

            # TODO regex magic?
            if ("X" not in line and "Y" not in line and
               "Z" not in line and " E" in line):
                not_removed = False
                continue

            if not_removed:
                data2.append(line)

        return data2

    def all_welder_control(self, lines: list[str]) -> list[str]:

        data2: list[str] = []
        seen_e = False

        for i in range(len(lines)):

            # Edge Cases
            if i - 1 < 0:
                data2.append(lines[i])
                continue
            if i + 1 == len(lines):
                data2.append(lines[i])
                continue

            # Might be better way to this? TODO
            if " E" in lines[i] and not seen_e:
                seen_e = True
                data2.append(GCodes.WELD_ON.value)
                e_index = lines[i].index(" E")
                data2.append(lines[i][0:e_index] + "\n")

            elif " E" in lines[i] and seen_e:
                e_index = lines[i].index(" E")
                data2.append(lines[i][0:e_index] + "\n")

            elif " E" not in lines[i] and seen_e:
                seen_e = False
                data2.append(GCodes.WELD_OFF.value)
                data2.append(lines[i])
            elif " E" not in lines[i] and not seen_e:
                data2.append(lines[i])

        return data2

    def move_up_z(self, lines: list[str]) -> list[str]:
        first_z = True
        diff = None

        data2: list[str] = []
        for line in lines:
            if " Z" in line:

                z_index = line.index("Z") + 1

                z_front: str = line[0:z_index]
                z_num = float(line[z_index:len(line)].replace(" ", "")
                              .replace("\n", ""))

                # TODO? Does this check lots of times seems slow
                if first_z:
                    diff = self.weld_gap - z_num
                    first_z = False
                if diff is None:
                    raise ValueError("""Difference between z_num
                                     and weld gap is None""")
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
    def add_sleep(self, lines: list[str]) -> list[str]:
        (ds, s) = modf(self.sleep_time)
        # Converts into ms
        ms = int(ds*1000)

        lines2: list[str] = []
        skip_first = True
        for line in lines:

            if line.startswith(";LAYER:"):
                self.sum_sleep_time += self.sleep_time

                if skip_first:
                    skip_first = False
                    continue
                lines2.append(f"{line}{GCodes.SLEEP.value} S{int(s)} P{ms}\n")

            elif line.startswith(";TIME_ELAPSED:"):
                time_elapsed = float(line[14:len(line)].replace("\n", ""))
                new_time_elapsed = time_elapsed+self.sum_sleep_time
                self.end_time = new_time_elapsed
                lines2.append(f";TIME_ELAPSED:{new_time_elapsed}")
            else:
                lines2.append(line)

        lines3: list[str] = []
        for line in lines2:
            if line.startswith(";TIME:"):
                lines3.append(f";TIME:{self.end_time}\n")
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
                for keyword in self.keywords:
                    value = self.getSettingValueByKey(keyword)
                    lines2.append(f';{keyword} = {value}\n')

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
        # TODO should log these settings into the GCode file
        self.weld_gap = float(self.getSettingValueByKey(self.keywords[0]))
        self.sleep_time = float(self.getSettingValueByKey(self.keywords[1]))

        try:
            lines = self.splitter(data)
            sleep = self.add_sleep(lines)
            no_extruder = self.remove_extruder(sleep)
            welder = self.all_welder_control(no_extruder)
            up_z = self.move_up_z(welder)
            settings = self.add_micer_settings(up_z)
            return settings
        except Exception as e:
            Logger.log("e", str(e))
            return ["\n\n\n\n", f'Error is "{str(e)}"', "\n\n\n\n"]
