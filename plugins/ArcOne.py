from ..Script import Script
from UM.Logger import Logger

logging_tag = "arcgcode_debug_arcone"


def cura_log(message: str, is_error: bool):
    log_type = "d" if is_error else "d"
    Logger.log(log_type, f"{logging_tag}: {message}")


try:
    import os
    import sys
    import pathlib
    from importlib.machinery import SourceFileLoader
    cura_log(f"before sys.path insert: Python Sys Path: {sys.path}", False)
    cura_log(f"curr wd {os.getcwd()}", False)

    # Assumes that the ArcOne is in the same directory as the repository
    src_dir = os.path.abspath(os.path.join(pathlib.Path(__file__).parent,
                                           "./src"))
    if not os.path.isdir(src_dir):
        raise Exception(f"could not find src directory: {src_dir}")

    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    cura_log(f"after sys.path insert: Python Sys Path: {sys.path}", False)
    import arcgcode
    cura_log(f"arcgcode init info: {arcgcode.__dict__}", False)
    raw_import_path = os.path.join(src_dir, "arcgcode", "__init__.py")
    raw_arcgcode = SourceFileLoader("arcgcode", raw_import_path).load_module()
    cura_log(f"raw_arcgcode init info: {raw_arcgcode.__dict__}", False)

    from arcgcode import v1
    cura_log(f"arcgcode.v1 init file: {v1.__file__}", False)

    from arcgcode.processor.base.version import ARCGCODE_VERSION
    cura_log("imported arcgcode successfully!", False)
    cura_log(f"VERSION: {ARCGCODE_VERSION}", False)
except Exception as e:
    cura_log(f"after error sys.path insert: Python Sys Path: {sys.path}",
             False)
    cura_log(f"error after sys.path insert: {str(e)}", True)


class ArcOne(Script):
    keywords = ["weldgap", "sleeptime", "rotate_amount", "movement_rate", "wait_for_temp"]

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
            },
            "movement_rate": {
                "label": "(NOT IMPLEMENTED YET) Set the Movement Rate (mm/min)",
                "description": "Set the movement rate (mm/min)",
                "type": "float",
                "default_value": 275.0,
                "minimum_value": 100.0
            },
            "wait_for_temp": {
                "label": "Set the temperature to wait for between layers",
                "description": "Sets the cool down temperature temperature (Celsius) that must be reached before starting new layer",
                "type": "float",
                "default_value": 275.0,
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
        debug_str = f"weld_gap: {weld_gap}, " + \
            f"sleep_time: {sleep_time}, rotate_amount: {rotate_amount}, " + \
            f" movement_rate: {movement_rate}, wait_for_temp: {wait_for_temp}"
        cura_log(debug_str, False)
        cura_log(f"{v1.CuraMicerSettings.__annotations__}", False)
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
        cura_log(f"data before: {data[:2]}", False)
        # For some reason, sometimes cura combines several commands into
        # a single entry in `data` (i.e. when the flavor is Griffin)
        #
        # Splitting it up manually here:
        parsed_data: list[str] = []
        for cmd in data:
            all_commands = cmd.split("\n")
            for split_cmd in all_commands:
                parsed_data.append(f"{split_cmd.strip()}\n")

        try:
            postprocessor = v1.CuraPostProcessor(self.get_settings())
            processed_gcode = postprocessor.execute(parsed_data)
            return processed_gcode
        except Exception as e:
            import json
            cura_log(str(e), True)
            return ["\n\n\n\n", f'Error is "{str(e)}"', "\n\n\n\n",
                    "with parsed data: " + json.dumps(parsed_data, indent=2)]
