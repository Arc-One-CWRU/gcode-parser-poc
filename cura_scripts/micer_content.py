# import re
from enum import Enum
from ..Script import Script
# Has to be place in
# C:\Program Files\UltiMaker Cura 5.4.0\share\
# cura\plugins\PostProcessingPlugin\scripts
# I made a symlink between there and the symlink_micer.py file


class GCodes(Enum):
    TOOL = "T0"
    SET_EXTRUDER_TEMP = "M104"
    SET_EXTRUDER_TEMP_AND_WAIT = "M109"
    SET_EXTRUDER_TO_RELAITVE = "M83"
    SET_EXTRUDER_TO_ABOSULTE = "M82"
    FAN_OFF = "M107"
    WELD_OFF = "M42 P1 S0 ;Disable Welder\n"
    WELD_ON = "M42 P1 S1 ;Enable Welder\n"


class Micer(Script):

    def getSettingDataString(self) -> str:
        # TODO make this JSON be compliant
        return """{
        "name": "Micer",
        "key": "Micer",
        "metadata":{},
        "version": 2,
        "settings":{
            "weldgap": {
                "label": "Set Weld Gap",
                "description": "Set the welding gap measured from base of gun to fixture (mm).",
                "type": "float",
                "default_value": 8,
                "minimum_value": 0,
                "maximum_value": 1000,
                "maximum_value_warning": 100
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

    # TODO Starting stuff gets moved but only some
    def splitter(self, data: list[str]) -> list[str]:
        """Splits the incoming data from Cura into a list
        with each element being a GCode"""
        lines2: list[str] = []
        for chunk in data:
            lines = chunk.split("\n")
            for line in lines:
                lines2.append(f'{line}\n')

        return lines2

    def execute(self, data: list[str]) -> list[str]:
        """ data is 4 + layer count elements long
            data[0] is the information about the print
            data[1] Start Commands
            data[2] -> data[n-3] each layer
            data[n-2] retracts extruder
            data[n-1] End Commands
        """

        self.weld_gap = float(self.getSettingValueByKey("weldgap"))
        try:
            lines = self.splitter(data)
            no_extruder = self.remove_extruder(lines)
            welder = self.all_welder_control(no_extruder)
            up_z = self.move_up_z(welder)
            return up_z
        except Exception as e:
            return ["\n\n\n\n", f'Error is "{str(e)}"', "\n\n\n\n"]
