from duetwebapi import DuetWebAPI
import time
# from Consts import URL

URL = "http://169.254.1.1"
duet = DuetWebAPI(URL)
duet.connect()
print("Connected")
start_time = 0
started_flag = False

while True:
    try:
        if duet.get_model("state.status") == "processing" and not started_flag:
            start_time = time.time()
            started_flag = True
        if duet.get_model("state.status") == "idle" and started_flag:
            end_time = time.time()
            print(f"{end_time-start_time} seconds")
            start_time = 0
            started_flag = False
    except ValueError:
        pass
