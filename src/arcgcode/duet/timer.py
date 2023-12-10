from duetwebapi import DuetWebAPI
from collections import defaultdict
import time
import atexit
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
        self.duet.connect()
        print("Connected")
    
    def run(self):
        start_time = 0
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
        while True:
            try:
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
                if (self.duet.get_status() == "processing" and
                   not started_flag):
                    print("Started Timer")
                    start_time = time.time()
                    started_flag = True
                if (self.duet.get_status() == "idle" and
                   started_flag):
                    end_time = time.time()
                    print(f"Print finished in {end_time-start_time} seconds")
                    start_time = 0
                    started_flag = False
            except Exception as e:
                if str(e) == "":
                    continue

                if str(e) != prev_err:
                    print("New Err: ", e)
                    prev_err = str(e)

            time.sleep(0.01)
