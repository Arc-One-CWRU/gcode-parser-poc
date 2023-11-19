from ..Script import Script
from UM.Logger import Logger

import sys
try:
    import os
    import pathlib

    Logger.log("e", f"arcgcode_debug_arcone: before sys.path insert: Python Sys Path: {sys.path}")
    Logger.log("e", f"arcgcode_debug_arcone: curr wd {os.getcwd()}")
    # Assumes that the ArcOne is in the same directory as the repository
    sys.path.append(os.path.abspath(os.path.join(pathlib.Path(__file__).parent,
                                                 "./src")))
    Logger.log("e", f"arcgcode_debug_arcone: after sys.path insert: Python Sys Path: {sys.path}")
    from arcgcode import v1
    Logger.log("e", "arcgcode_debug_arcone: imported arcgcode successfully!")
except Exception as e:
    Logger.log("e", f"arcgcode_debug_arcone: after sys.path insert: Python Sys Path: {sys.path}")
    Logger.log("e", f"arcgcode_debug_arcone: after sys.path insert: {str(e)}")


class ArcOne(Script):
    keywords = ["weldgap", "sleeptime", "rotate_amount"]

    def getSettingDataString(self) -> str:
        return """{
        "name": "ArcOne",
        "key": "ArcOne",
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
            },
            "rotate_amount": {
                "label": "Set the Rotate Count",
                "description": "Set the amount of times to rotate.",
                "type": "int",
                "default_value": 6,
                "minimum_value": 0
            }
        }
        }"""

    def get_settings(self) -> v1.CuraMicerSettings:
        weld_gap = float(self.getSettingValueByKey(self.keywords[0]))
        sleep_time = float(self.getSettingValueByKey(self.keywords[1]))
        rotate_amount = int(self.getSettingValueByKey(self.keywords[2]))
        debug_str = f"arcgcode_debug: weld_gap: {weld_gap}, " + \
            f"sleep_time: {sleep_time}, rotate_amount: {rotate_amount}"
        Logger.log("e", debug_str)

        settings = v1.CuraMicerSettings(weld_gap=weld_gap,
                                        sleep_time=sleep_time,
                                        rotate_amount=rotate_amount)
        return settings

    # TODO could use a helper to get numbers out of lines

    def execute(self, data: list[str]) -> list[str]:
        """ data is 4 + layer count elements long
            data[0] is the information about the print
            data[1] Start Commands
            data[2] -> data[n-3] each layer
            data[n-2] retracts extruder
            data[n-1] End Commands
        """
        micer = v1.CuraPostProcessor(self.get_settings())

        try:
            settings = micer.execute(data)
            return settings
        except Exception as e:
            Logger.log("e", str(e))
            return ["\n\n\n\n", f'Error is "{str(e)}"', "\n\n\n\n"]
