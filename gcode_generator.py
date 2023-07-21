import os
from typing import Optional
import argparse
from datetime import datetime

HOME = "G28"
DIR = "generated"

SLEEP_START = "G4"

ENABLE = "M42 P1 S1"
DISABLE = "M42 P1 S0"
NEWLINE = "\n"


class GCODEGenerator:

    def __init__(self) -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument("-w", "--weld_gap", help="Weld gap distance (mm).",
                            type=float, default=8)
        parser.add_argument("-wh", "--weld_layer_height", help="Weld height distance (mm).",
                            type=float, default=2)
        parser.add_argument("-ww", "--weld_layer_width", help="Weld width distance (mm).",
                            type=float, default=2)
        parser.add_argument("-ts", "--transport_speed", help="Set transport speed (mm).",
                            type=float)
        parser.add_argument("-ps", "--print_speed", help="Set print speed (mm).",
                            type=float)
        
        parser.add_argument("-x", "--x_size", help="Set print speed (mm).",
                            type=float)
        parser.add_argument("-y", "--y_size", help="Set print speed (mm).",
                            type=float)
        parser.add_argument("-z", "--z_size", help="Set print speed (mm).",
                            type=float)
        
        parser.add_argument("-v", "--verbose", action="store_true",
                            help="Debug logging.")
        args = parser.parse_args()

        print(args.input_dir)

    def run(self):
        filename = f"{str(datetime.now())[:-7]}.gcode".replace(" ", " Time=").replace(":", " ")
        with open(os.path.join(DIR, filename), "x") as f:

            f.write("test)")

    def add_sleep(self, milliseconds: Optional[float] = None, seconds: Optional[int] = None):
        pass


if __name__ == "__main__":
    gen = GCODEGenerator()
    gen.run()
