from ..Script import Script
from UM.Logger import Logger

logging_tag = "arcgcode_debug_arcone"


def cura_log(message: str, is_error: bool):
    log_type = "d" if is_error else "d"
    Logger.log(log_type, f"{logging_tag}: {message}")


try:
    import os
    import json
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
    keywords = ["weldgap", "sleeptime", "rotate_amount",
                "overwrite_movement_rate", "movement_rate",
                "use_temperature_sensor", "wait_for_temp", "pause_after_layer"]

    def getSettingDataString(self) -> str:
        script_name = "ArcOne"
        options = {
            "weldgap": {
                "label": "Set Weld Gap",
                "description": "Set the welding gap.",
                "unit": "mm",
                "type": "float",
                "default_value": 8,
                "minimum_value": 0,
                "maximum_value": 1000,
                "maximum_value_warning": 100
            },
            "sleeptime": {
                "label": "Set Sleep Time",
                "description": "Set the layer sleep time.",
                "unit": "s",
                "type": "float",
                "default_value": 30,
                "minimum_value": 0,
                "enabled": "not use_temperature_sensor",
            },
            "rotate_amount": {
                "label": "Set the Rotate Count",
                "description": "Set the amount of times to rotate.",
                "unit": "times",
                "type": "int",
                "default_value": 6,
                "minimum_value": 0
            },
            "overwrite_movement_rate": {
                "label": "Overwrite G-Code Movement Rate",
                "description": "Enable this option when you want to " +
                "overwrite the existing G-Code movement rates. This is " +
                "useful for testing simple prints.",
                "type": "bool",
                "default_value": False,
                "enabled": True,
            },
            "movement_rate": {
                "label": "Constant Movement Rate",
                "description": "Sets the extruder movement rate (Default 1035 mm/min)",
                "unit": "mm/min",
                "type": "float",
                "default_value": 1035,
                "minimum_value": 0.0,
                # Only show movement_rate option when
                # overwrite_movement_rate is true.
                "enabled": "overwrite_movement_rate"
            },
            "use_temperature_sensor": {
                "label": "Use Temperature Sensor",
                "description": "Enable this to toggle on temperature " +
                "sensor options",
                "type": "bool",
                "default_value": False,
                "enabled": True,
            },
            "wait_for_temp": {
                "label": "Set the temperature to wait for between layers",
                "description": "Sets the cool down temperature temperature " +
                "that must be reached before starting new layer",
                "unit": "°C",
                "type": "float",
                "default_value": 275.0,
                "minimum_value": 0,
                "enabled": "use_temperature_sensor"
            },
            "pause_after_layer": {
                "label": "Pause after each layer until manually resumed",
                "description": " Pause after each layer until manually resumed",
                "type": "bool",
                "default_value": False,
                "enabled": True,
            },

             "return_home": {
                "label": "Return to home button",
                "description": "Return to home after print finishes",
                "type": "bool",
                "default_value": False,
                "enabled": True,
            },



        }

        settings = {
            "name": script_name,
            "key": script_name,
            "metadata": {},
            "version": 2,
            "settings": options,
        }

        json_str = json.dumps(settings)
        return json_str

    def get_settings(self) -> v1.CuraMicerSettings:
        weld_gap = float(self.getSettingValueByKey(self.keywords[0]))
        sleep_time = float(self.getSettingValueByKey(self.keywords[1]))
        rotate_amount = int(self.getSettingValueByKey(self.keywords[2]))
        overwrite_movement_rate = bool(self.getSettingValueByKey(self.keywords[3]))
        movement_rate = float(self.getSettingValueByKey(self.keywords[4]))
        use_temperature_sensor = bool(self.getSettingValueByKey(self.keywords[5]))
        wait_for_temp = float(self.getSettingValueByKey(self.keywords[6]))
        pause_after_layer = bool(self.getSettingValueByKey(self.keywords[7]))
        return_home = bool(self.getSettingValueByKey(self.keywords[8]))

        debug_str = f"weld_gap: {weld_gap}, " + \
            f"sleep_time: {sleep_time}, rotate_amount: {rotate_amount}, " + \
            f"overwrite_movement_rate: {overwrite_movement_rate}, " + \
            f"use_temperature_sensor: {use_temperature_sensor}, " + \
            f"movement_rate: {movement_rate}, wait_for_temp: {wait_for_temp}, " + \
            f"pause_after_layer: {pause_after_layer}, " + \
            f"return_home: {return_home}"

        cura_log(debug_str, False)
        cura_log(f"{v1.CuraMicerSettings.__annotations__}", False)
        settings = v1.CuraMicerSettings(weld_gap=weld_gap,
                                        sleep_time=sleep_time,
                                        rotate_amount=rotate_amount,
                                        overwrite_movement_rate=overwrite_movement_rate,
                                        movement_rate=movement_rate,
                                        use_temperature_sensor=use_temperature_sensor,
                                        wait_for_temp=wait_for_temp,
                                        pause_after_layer=pause_after_layer,
                                        return_home =return_home,
                                        )
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
                stripped_cmd = split_cmd.strip()
                if stripped_cmd != "":
                    parsed_data.append(f"{stripped_cmd}\n")

        try:
            postprocessor = v1.CuraPostProcessor(self.get_settings())
            processed_gcode = postprocessor.execute(parsed_data)
            return processed_gcode
        except Exception as e:
            import json
            cura_log(str(e), True)
            return ["\n\n\n\n", f'Error is "{str(e)}"', "\n\n\n\n",
                    "with parsed data: " + json.dumps(parsed_data, indent=2)]
