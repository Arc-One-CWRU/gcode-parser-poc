from duetwebapi import DuetWebAPI
from collections import defaultdict
import time
import atexit
import requests
import pandas as pd
from pathlib import Path
import copy
# from Consts import URL

ARC_ONE_DUET_URL = "http://192.168.0.4"


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
        self.gcode_file_name = None
    
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
                    self.gcode_file_name = Path(fileName).stem
                    print("tried to read file with name: ", self.gcode_file_name)
                    rawFile = self.duet.get_file(filename=self.gcode_file_name + ".gcode", binary=False)
                    #print(rawFile)
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
        prev_layer = self.duet.get_layer()
        # Key: Layer
        # Values: defaultdict(float)
        #   start -> start timestamp (s)
        #   end -> end timestamp (s)
        #   duration -> s
        layer_times = {
            0: defaultdict(float, {
                "start": time.time(),
            })
        }

        prev_err = "RANDOM_PLACEHOLDER_ERROR"
        start_time = time.time()
        
        raw_gcode_file = self.get_gcode_file()
        message = self.duet.get_messagebox()
        temp_times = []
        times = []
        interpass_temps = []
        weld_contorl_layer = 0
        interpass = False
        while True:
            try:
                # message4 = self.duet.get_messagebox()
                # print(message4)
                # if message4 == None:
                #     print("d;askfjasd;jflkj")
                # if type(message4) == None:
                #     print("wepuirqrupoiu")
                if self.duet.get_status() == "processing" and not started_flag:
                    print("Started Timer")
                    start_time = time.time()
                    print(start_time)
                    started_flag = True
                
                
                curr_layer = self.duet.get_layer()
                if curr_layer != layer:
                    layer_times[curr_layer] = defaultdict(float, {
                            "start": time.time(),
                        })
                    layer_times[layer]["end"] = time.time()
                    layer = curr_layer
                     
                message2 = self.duet.get_messagebox()
                if message2 != message:
                    
                    print(message2)
                    print(message2["message"])
                    
                    if message2["message"].startswith("Weld"):                        
                        b_index = message2["message"].find("B")
                        l_index = message2["message"].find("L")                    
                        temp_layer = int(message2["message"][l_index+1:b_index-1])
                        if temp_layer != weld_contorl_layer:
                            weld_contorl_layer += 1
                            times.append(temp_times)
                            temp_times.clear()
                        temp_times.append(time.time())
                        print(temp_times)
                    if message2["message"].startswith("Interpass Start"):
                        layer_times[layer]["interpass_start"] = time.time()
                        interpass = True
                        message2 = self.duet.get_messagebox()
                        temp_temps = []
                        time_temps = []
                        while not message2["message"].startswith("Interpass End"):
                            try:
                                message3 = self.duet.get_messagebox()
                            except:
                                print("this makes no sense")
                            if message3 != None:
                                print(message3)
                                message2 = copy.deepcopy(message3)
                            time_temp = time.time()
                            temp = self.duet.get_temperatures()
                            print(temp[2]["lastReading"])
                            time_temps.append(time_temp)
                            temp_temps.append(temp[2]["lastReading"])
                            time.sleep(.2)
                            
                        layer_times[layer]["interpass_end"] = time.time()
                        print(time_temps)
                        interpass_temps.append(time_temps)
                        interpass_temps.append(temp_temps)
                        print(interpass_temps)
                message = message2

                if self.duet.get_status() == "idle" and started_flag:
                    layer_times[layer]["end"] = time.time()
                    end_time = time.time()
                    total_time = end_time - start_time
                    started_flag = False
                    total_weld_time = 0
                    data = []
                    max_beads = 0
                    total_interpass_time = 0
                    for i in range(len(times)):
                        print(i)
                        print(times[i])
                    print("break")
                    for i in times:
                        print(i)
                    #print(f"Length of times[4] {len(times[4])}")
                    print(len(layer_times))
                    for i in range(2, len(layer_times)):
                        print(layer_times[i])    
                        print(i)
                        layer_weld_time = 0
                        arr = [i-1]
                        arr.append(layer_times[i]["start"])
                        arr.append(layer_times[i]["end"])
                        arr.append(layer_times[i]["end"]-layer_times[i]["start"])
                        curr_max_beads = 0
                        for j in range(0, len(times[i-2]), 2):
                            curr_max_beads += 1
                            if curr_max_beads > max_beads:
                                max_beads = curr_max_beads
                            print(f"Here i{i} j{j}")
                            arr.append(times[i-2][j])
                            arr.append(times[i-2][j+1])
                            weld_time = times[i-2][j+1]-times[i-2][j]
                            arr.append(weld_time)
                            layer_weld_time += weld_time
                            total_weld_time += weld_time
                        arr.append(layer_weld_time)
                        if interpass:
                            arr.append(layer_times[i]["interpass_start"])
                            arr.append(layer_times[i]["interpass_end"])
                            arr.append(layer_times[i]["interpass_end"]-layer_times[i]["interpass_start"])
                            total_interpass_time += layer_times[i]["interpass_end"]-layer_times[i]["interpass_start"]
                        data.append(arr)
                    columns = ["Layer", "Layer Start", "Layer End", "Layer Duration"]
                    totals = ["Totals", start_time, end_time, total_time]
                    for i in range(max_beads):
                        columns.append(f"Bead {i+1} Start")
                        columns.append(f"Bead {i+1} End")
                        columns.append(f"Bead {i+1} Weld Duration")
                        totals.append("N/A")
                        totals.append("N/A")
                        totals.append("N/A")
                    columns.append("Total Weld Duration")
                    totals.append(total_weld_time)
                    if interpass:
                        columns.append("Interpass Start")
                        columns.append("Interpass End")
                        columns.append("Interpass Duration")
                        totals.append("N/A")
                        totals.append('N/A')
                        totals.append(total_interpass_time)
                                     
                    data.insert(0, totals)
                    time_df = pd.DataFrame(data, columns=columns)
                    time_file_path = f"C:\\Users\\Arc One\\Desktop\\TimeData\\{self.gcode_file_name}TimeData.csv"
                    time_df.to_csv(time_file_path)
                    print(f"Time data can be found at {time_file_path}")
                    
                    if interpass:
                        print(interpass_temps)
                        interpass_columns = []
                        for i in range(0, len(interpass_temps), 2):
                            interpass_columns.append(f"Interpass {int((i+3)/2)} Time (Between layers {int((i+3)/2)} and {int((i+4)/2)})")
                            interpass_columns.append(f"Interpass {int((i+3)/2)} Temperature (Between layers {int((i+3)/2)} and {int((i+4)/2)})")
                        print("dsfjk")
                        print(interpass_columns)
                        temp_temperature_df = pd.DataFrame(interpass_temps)
                        temperature_df = temp_temperature_df.T

                        temperature_file_path = f"C:\\Users\\Arc One\\Desktop\\InterpassData\\{self.gcode_file_name}InterpassData.csv"
                        temperature_df.columns = interpass_columns
                        temperature_df.to_csv(temperature_file_path)
                        print(f"Interpass data can be found at {temperature_file_path}")

                    print("Print End")

                

                # if (self.duet.get_status() == "processing" and
                #    not started_flag):
                #     print("Started Timer")
                #     #start_time = time.time()
                #     started_flag = True
                # #print(self.duet.get_status())
                # #print(started_flag)
                # #if self.duet.get_status() == "idle":
                #     #print("HEREREWQRWQERQWERQWREW")
                    
                # if (self.duet.get_status() == "idle" and started_flag):
                #     print(f"dsafjhdsakfjljsf {max_beads}")
                #     end_time = time.time()
                #     layer_times[layer]["end"] = end_time
                #     total_time = end_time - start_time
                #     print(f"Print finished in {total_time} seconds")
                #     started_flag = False
                #     layer_arr = []
                #     total_weld_time = 0
                #     for layer in layer_times:
                #         arr = [layer]
                #         arr.append(layer_times[layer]["start"])
                #         arr.append(layer_times[layer]["end"])
                #         #arr.append(layer_times[layer]["duration"])
                #         print()
                #         for i in range(max_beads-1):
                #             if layer == len(layer_times)-1 and i == max_beads-2:
                #                 layer_times[layer]["end" + str(i)] = end_time
                #             arr.append(layer_times[layer]["begin" + str(i)])
                #             arr.append(layer_times[layer]["end" + str(i)])
                #             arr.append(layer_times[layer]["end" + str(i)] - layer_times[layer]["begin" + str(i)])
                #             total_weld_time += layer_times[layer]["end" + str(i)] - layer_times[layer]["begin" + str(i)]
                #         # arr.append(layer_times[layer]["Weld_Start"])
                #         # arr.append(layer_times[layer]["Weld_End"])
                #         #arr.append(layer_times[layer]["Weld_End"] - layer_times[layer]["Weld_Start"])
                #         #total_weld_time += layer_times[layer]["Weld_End"] - layer_times[layer]["Weld_Start"]
                #         layer_arr.append(arr)
                #     #columns = ["Totals", layer_times[1]"start"], end_time, 
                #     layer_arr.insert(0,["Totals", layer_times[1]["start"], end_time, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", total_weld_time])
                #     df = pd.DataFrame(layer_arr, columns=["Layer", "Start", "End", "Weld_Start1", "Weld_End1", "Weld_Total1", "Weld_Start2", "Weld_End2", "Weld_Total2", "Weld_Start3", "Weld_End3", "Weld_Total3", "Weld_Duration"])
                #     df.to_csv(f"C:\\Users\\Arc One\\Desktop\\TimeData\\{self.gcode_file_name}TimeData.csv")
                
            except Exception as e:
                if str(e) == "":
                    continue

                if str(e) != prev_err:
                    print("New Err: ", e)
                    prev_err = str(e)
                    

            #time.sleep(0.001)
        
        

