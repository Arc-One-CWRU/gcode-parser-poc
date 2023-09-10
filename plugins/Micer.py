from ..Script import Script
from UM.Logger import Logger
# Has to be place in
# C:\Program Files\UltiMaker Cura 5.4.0\share\
# cura\plugins\PostProcessingPlugin\scripts
# I made a symlink between there and the symlink_micer.py file

import sys

try:
    import os
    Logger.log("e", f"arcgcode_debug: curr wd {os.getcwd()}")
    repo_dir = os.getenv("GCODE_REPO_DIR")
    Logger.log("e", f"arcgcode_debug: env var: {repo_dir}")
    if repo_dir == None:
        raise Exception("env var GCODE_REPO_DIR should not be None")
    sys.path.append(os.path.abspath(repo_dir).strip('"').strip())
    from arcgcode import v1
    Logger.log("e", "arcgcode_debug: imported arcgcode successfully!")
except Exception as e:
    Logger.log("e", f"arcgcode_debug: after sys.path insert: Python Sys Path: {sys.path}")
    Logger.log("e", f"arcgcode_debug: after sys.path insert: {str(e)}")


class Micer(Script):
    keywords = ["weldgap", "sleeptime", "rotate_amount"]

    def getSettingDataString(self) -> str:
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
        micer = v1.CuraMicer(self.get_settings())

        try:
            settings = micer.execute(data)
            return settings
        except Exception as e:
            Logger.log("e", str(e))
            return ["\n\n\n\n", f'Error is "{str(e)}"', "\n\n\n\n"]
