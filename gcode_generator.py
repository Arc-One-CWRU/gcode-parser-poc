import os
from typing import Optional
import argparse
from datetime import datetime

HOME = "G28"
DIR = "generated"

SLEEP_START = "G4"

ENABLE = "M42 P1 S1"
DISABLE = "M42 P1 S0"


class GCODEGenerator:

    def __init__(self) -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument("-i", "--input_dir", help="Input directory of GCodes to transform.",
                            type=str)
        parser.add_argument("-o", "--output_dir", help="Output directory where the parsed GCodes will go.",
                            type=str)
        parser.add_argument("-v", "--verbose", action="store_true",
                            help="Debug logging.")
        args = parser.parse_args()

        print(args.input_dir)

    def run(self):

        with open(os.path.join(DIR, f"{datetime.now()}.gcode").replace(" ", ""), "x") as f:

            f.write("test)")
            f.write("pog)")

    def add_sleep(self, milliseconds: Optional[float] = None, seconds: Optional[int] = None):
        pass


if __name__ == "__main__":
    gen = GCODEGenerator()
    gen.run()
