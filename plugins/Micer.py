from ..Script import Script
from UM.Logger import Logger
# Has to be place in
# C:\Program Files\UltiMaker Cura 5.4.0\share\
# cura\plugins\PostProcessingPlugin\scripts
# I made a symlink between there and the symlink_micer.py file

import sys
try:
    import os
    import pathlib

    Logger.log("e", f"arcgcode_debug_micer: before sys.path insert: Python Sys Path: {sys.path}")
    Logger.log("e", f"arcgcode_debug_micer: curr wd {os.getcwd()}")
    # Assumes that the Micer is in the same directory as the repository
    sys.path.append(os.path.abspath(os.path.join(pathlib.Path(__file__).parent,
                                                 "./src")))
    Logger.log("e", f"arcgcode_debug_micer: after sys.path insert: Python Sys Path: {sys.path}")
    from arcgcode import v1
    Logger.log("e", "arcgcode_debug_micer: imported arcgcode successfully!")
except Exception as e:
    Logger.log("e", f"arcgcode_debug_micer: after sys.path insert: Python Sys Path: {sys.path}")
    Logger.log("e", f"arcgcode_debug_micer: after sys.path insert: {str(e)}")


class Micer(Script):
    keywords = ["weldgap", "sleeptime", "rotate_amount", "movement_rate", "wait_for_temp"]

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
            },
            "movement_rate": {
                "label": "(NOT IMPLEMENTED YET) Set the Movement Rate (mm/min)",
                "description": "Set the movement rate (mm/min)",
                "type": "float",
                "default_value": 275.0,
                "minimum_value": 100.0
            },
            "wait_for_temp": {
                "label": "Set the cool down temperature between each layer (Celsius)",
                "description": "Sets the temperature that must be reached before starting new layer",
                "type": "float",
                "defualt_value": 275.0,
                "minimum_value": 35
            }
        }
        }"""
    
    def get_settings(self) -> v1.CuraMicerSettings:
        weld_gap = float(self.getSettingValueByKey(self.keywords[0]))
        sleep_time = float(self.getSettingValueByKey(self.keywords[1]))
        rotate_amount = int(self.getSettingValueByKey(self.keywords[2]))
        movement_rate = float(self.getSettingValueByKey(self.keywords[3]))
        wait_for_temp = float(self.getSettingValueByKey(self.keywords[4]))

        debug_str = f"arcgcode_debug: weld_gap: {weld_gap}, " + \
            f"sleep_time: {sleep_time}, rotate_amount: {rotate_amount}, movement_rate: {movement_rate}, wait_for_temp: {wait_for_temp}"
        Logger.log("e", debug_str)

        settings = v1.CuraMicerSettings(weld_gap=weld_gap,
                                        sleep_time=sleep_time,
                                        rotate_amount=rotate_amount,
                                        movement_rate=movement_rate,
                                        wait_for_temp=wait_for_temp)
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
