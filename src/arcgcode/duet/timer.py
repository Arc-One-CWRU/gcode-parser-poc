from duetwebapi import DuetWebAPI
from collections import defaultdict
import time
import atexit
import requests
import pandas as pd
from pathlib import Path
# from Consts import URL

ARC_ONE_DUET_URL = "http://169.254.1.1"


class DuetTimer(object):
    """Times different actions of each print and layer and exports the data to
    CSV.

    Useful documentation:
    https://reprap.org/wiki/RepRap_Firmware_Status_responses
    """
    def __init__(self, url: str) -> None:
        self.duet = DuetWebAPI(url)
        self.url = url
        self.duet.connect()
        print("Connected")
    
    def get_reply(self):
        url = f'{self.url}/rr_reply'
        r = requests.get(url)
        if not r.ok:
            raise ValueError
        return r.text
    
    def get_gcode_file(self):
        """Get a job model until a filename is not None (print started)
        """
        fileName = None
        while fileName is None:
            model = self.duet.get_model("job")
            if model["file"] is not None:
                fileName = model["file"]["fileName"]
                if fileName is not None:
                    print("Filename: ", fileName)
                    gcode_file_name = Path(fileName).name
                    print("tried to read file with name: ", gcode_file_name)
                    rawFile = self.duet.get_file(filename=gcode_file_name, binary=True)
                    return rawFile

    def run(self):
        start_time = 0
        end_time = 0
        total_time = 0
        started_flag = False
        atexit.register(self.duet.disconnect)

        num_tools = self.duet.get_num_tools()
        print(f"Num Tools: {num_tools}")
        curr_tool = self.duet.get_current_tool()
        print(f"Current Tool: {curr_tool}")
        layer = self.duet.get_layer()
        # Key: Layer
        # Values: defaultdict(float)
        #   start -> start timestamp (s)
        #   end -> end timestamp (s)
        #   duration -> s
        layer_times = {
            0: defaultdict(float, {
                "start": time.time()
            })
        }

        prev_err = "RANDOM_PLACEHOLDER_ERROR"

        raw_gcode_file = self.get_gcode_file()
        model = self.duet.get_model("job")

        while True:
            try:
                line = ""
                model2 = self.duet.get_model("job")
                if model["filePosition"] != model2["filePosition"]:
                    print(f"model {model2}")
                    model = model2
                    file_position = model["filePosition"]
                    new_line_position = raw_gcode_file.find(b'\n', file_position)
                    line = raw_gcode_file[file_position:new_line_position]                       
                    print(f"Line: {raw_gcode_file[file_position:new_line_position]}")

                curr_layer = self.duet.get_layer()
                
                
                if curr_layer != layer:
                    layer_end_time = time.time()
                    layer_start_time = layer_times[layer]["start"]
                    layer_duration = layer_end_time - layer_start_time
                    layer_times[layer]["end"] = layer_end_time
                    layer_times[layer]["duration"] = layer_duration
                    print(f"Changed from layer {layer} to layer {curr_layer}, total duration: {layer_duration}")
                    layer = curr_layer
                    layer_times[layer] = defaultdict(float, {
                        "start": time.time(),
                    })
                else:
                    temp_time = time.time()
                    if line.startswith("M42 P1 S1") and "Weld_Start" not in layer_times[layer]:
                        layer_times[layer]["Weld_Start"] = temp_time
                    elif line.startswith("M42 P1 S0"):
                        layer_times[layer]["Weld_End"] = temp_time
                if (self.duet.get_status() == "processing" and
                   not started_flag):
                    print("Started Timer")
                    start_time = time.time()
                    started_flag = True
                if (self.duet.get_status() == "idle" and
                   started_flag):
                    end_time = time.time()
                    total_time = end_time - start_time
                    print(f"Print finished in {total_time} seconds")
                    start_time = 0
                    started_flag = False
                
            except Exception as e:
                if str(e) == "":
                    continue

                if str(e) != prev_err:
                    print("New Err: ", e)
                    prev_err = str(e)

            time.sleep(0.01)
        
        layer_arr = []
        total_weld_time = 0
        for layer, dic in enumerate(layer_times):
            arr = [layer]
            arr.append(layer_times[layer]["start"])
            arr.append(layer_times[layer]["end"])
            arr.append(layer_times[layer]["duration"])
            arr.append(layer_times[layer]["Weld_Start"])
            arr.append(layer_times[layer]["Weld_End"])
            arr.append(layer_times[layer]["Weld_End"] - layer_times[layer]["Weld_Start"])
            total_weld_time += layer_times[layer]["Weld_End"] - layer_times[layer]["Weld_Start"]
            layer_arr.append(arr)
        layer_arr.insert(0,["Totals", start_time, endtime, total_time, "N/A", "N/A", total_weld_time])
        df = pd.DataFrame(layer_arr, columns=["Layer", "Start", "End", "Duration", "Weld_Start", "Weld_End", "Weld_Duration"])


