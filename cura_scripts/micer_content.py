# import re
from enum import Enum
from ..Script import Script
# Has to be place in C:\Program Files\UltiMaker Cura 5.4.0\share\cura\plugins\PostProcessingPlugin\scripts
# For ease of coding I made a symlink between there and the cura_scripts directory


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
        return """{
        "name": "Micer",
        "key": "Micer",
        "metadata":{},
        "version": 2,
        "settings":{}
        }"""

    def remove_extruder(self, data: list[str]) -> list[str]:

        # TODO Write wrapper for splitting into lines
        data2: list[str] = []
        for chunk in data:
            lines = chunk.split("\n")
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

                line += "\n"

                if not_removed:
                    data2.append(line)

        return data2

    def all_welder_control(self, data: list[str]) -> list[str]:

        data2: list[str] = []
        seen_e = False

        for i in range(len(data)):

            # Edge Cases
            if i - 1 < 0:
                data2.append(data[i])
                continue
            if i + 1 == len(data):
                data2.append(data[i])
                continue

            # Might be better way to this? TODO
            if " E" in data[i] and not seen_e:
                seen_e = True
                data2.append(GCodes.WELD_ON.value)
                e_index = data[i].index(" E")
                data2.append(data[i][0:e_index] + "\n")

            elif " E" in data[i] and seen_e:
                e_index = data[i].index(" E")
                data2.append(data[i][0:e_index] + "\n")

            elif " E" not in data[i] and seen_e:
                seen_e = False
                data2.append(data[i])
                data2.append(GCodes.WELD_OFF.value)
            elif " E" not in data[i] and not seen_e:
                data2.append(data[i])

        return data2

    def execute(self, data: list[str]) -> list[str]:
        """ data is 4 + layer count elements long
            data[0] is the information about the print
            data[1] Start Commands
            data[2] -> data[n-3] each layer
            data[n-2] retracts extruder
            data[n-1] End Commands
        """

        no_extruder = self.remove_extruder(data)
        return self.all_welder_control(no_extruder)
