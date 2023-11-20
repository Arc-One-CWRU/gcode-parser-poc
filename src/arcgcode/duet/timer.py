from duetwebapi import DuetWebAPI
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
        while True:
            try:
                if (self.duet.get_model("state.status") == "processing" and
                   not started_flag):
                    print("Started Timer")
                    start_time = time.time()
                    started_flag = True
                if (self.duet.get_model("state.status") == "idle" and
                   started_flag):
                    end_time = time.time()
                    print(f"Print finished in{end_time-start_time} seconds")
                    start_time = 0
                    started_flag = False
            except ValueError:
                pass
