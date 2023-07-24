import os
from argparse import ArgumentParser
from datetime import datetime
from io import TextIOWrapper
from typing import Optional
from math import ceil
from duetwebapi import DuetWebAPI

MOVE = "G0"
LINEAR_MOVE = "G1"
HOME = "G28\n"

SLEEP_START = "G4"

WELDER_CONTROL = "M42 P1"


DIR = "generated"


class GCODEGenerator:

    def __init__(self) -> None:
        parser = ArgumentParser()
        parser.add_argument("-w", "--weld_gap", help="Weld gap distance (mm).",
                            type=float, default=8)
        parser.add_argument("-wh", "--weld_layer_height", help="Weld height distance (mm).",
                            type=float, default=2.3)
        parser.add_argument("-ww", "--weld_layer_width", help="Weld width distance (mm).",
                            type=float, default=8.5)

        parser.add_argument("-wlo", "--weld_layer_overlap", help="Overlap between weld lines (mm).",
                            type=float)

        parser.add_argument("-ts", "--travel_speed", help="Set transport speed (mm/min).",
                            type=float)
        parser.add_argument("-ps", "--print_speed", help="Set print speed (mm/min).",
                            type=float, default=381)

        # Overall Dimensions of bed
        parser.add_argument("-xbs", "--x_bed_size", help="Set x bed size (mm).",
                            type=float, default=580)
        parser.add_argument("-ybs", "--y_bed_size", help="Set y bed size (mm).",
                            type=float, default=240)
        parser.add_argument("-zbs", "--z_bed_size", help="Set z bed size (mm).",
                            type=float, default=180)

        # Overall Dimensions of print
        parser.add_argument("-x", "--x_size", help="Set x size (mm).",
                            type=float)
        parser.add_argument("-y", "--y_size", help="Set y size (mm).",
                            type=float)
        parser.add_argument("-z", "--z_size", help="Set z size (mm).",
                            type=float)

        # Location of Corner of print
        parser.add_argument("-xc", "--x_corner", help="Set x corner (mm).",
                            type=float)
        parser.add_argument("-yc", "--y_corner", help="Set y corner (mm).",
                            type=float)

        # Z Clearance
        parser.add_argument("-zc", "--z_clearance", help="Set z clearance for raising overstuff (mm).",
                            type=float)

        parser.add_argument("-v", "--verbose", help="Debug logging.",
                            type=bool, default=False)
        self.args = parser.parse_args()

        for kwarg in self.args._get_kwargs():
            if kwarg[1] is None:
                raise ValueError(f"{kwarg[0]} is None")

        self.filename = f"{str(datetime.now())[:-7]}.gcode".replace(" ", " Time=").replace(":", " ")
        with open(os.path.join(DIR, self.filename), "x") as f:
            self.run(f)

    def safety_checks(self):
        if self.args.x_size > self.args.x_bed_size or self.args.x_corner > self.args.x_bed_size:
            raise ValueError("X dimension does not fit in bed")

        if self.args.y_size > self.args.y_bed_size or self.args.y_corner > self.args.y_bed_size:
            raise ValueError("Y dimension does not fit in bed")

        if self.args.z_size + self.args.z_clearance > self.args.z_bed_size:
            raise ValueError("Z dimension does not fit in bed")

    def run(self, file: TextIOWrapper):
        self.safety_checks()
        self.write_info(file)
        self.write_volume(file)
        self.write_config(file)

    def write_info(self, file: TextIOWrapper):
        file.write(";Print Information\n")
        file.write(f";Weld Gap = {self.args.weld_gap} mm\n")
        file.write(f";Weld Height = {self.args.weld_layer_height} mm\n")
        file.write(f";Weld Width = {self.args.weld_layer_width} mm\n")
        file.write(f";Weld Layer Overlap = {self.args.weld_layer_overlap} mm\n")
        file.write(f";Transport Speed = {self.args.travel_speed} mm\n")
        file.write(f";Print Speed = {self.args.print_speed} mm\n")
        file.write(f";X Bed Size = {self.args.x_bed_size} mm\n")
        file.write(f";Y Bed Size = {self.args.y_bed_size} mm\n")
        file.write(f";Z Bed Size = {self.args.z_bed_size} mm\n")
        file.write(f";X Size = {self.args.x_size} mm\n")
        file.write(f";Z Size = {self.args.z_size} mm\n")
        file.write(f";Y Size = {self.args.y_size} mm\n")
        file.write(f";X Corner = {self.args.x_corner} mm\n")
        file.write(f";Y Corner = {self.args.y_corner} mm\n")
        file.write(f";Z Clearance = {self.args.z_clearance} mm\n")
        file.write(f";Logging enabled? = {self.args.verbose}\n")

    def write_volume(self, file: TextIOWrapper):
        # Move home
        file.write(HOME)

        # Raise to avoid junk on table
        self.add_linear_move(file, self.args.travel_speed, z=self.args.z_clearance)

        # Move above starting position
        self.add_rapid_move(file, self.args.travel_speed, self.args.x_corner, self.args.y_corner)

        # Move into starting position
        self.add_linear_move(file, 100, z=self.args.weld_gap)

        # x_gap_between_lines: float = (self.args.weld_layer_width - 

        x_line_count: int = ceil(self.args.y_size / self.args.weld_layer_overlap)
        z_line_count: int = ceil(self.args.z_size / self.args.weld_layer_height)

        x_pos = self.args.x_corner
        y_pos = self.args.y_corner
        z_pos = self.args.weld_gap

        for _ in range(z_line_count):
            for _ in range(x_line_count):

                # Settle in
                self.add_sleep(file, seconds=1)

                # Enable welder
                self.control_welder(file, 1)

                # Moves a long line
                self.add_linear_move(file, self.args.print_speed, y=(y_pos + self.args.y_size))

                # Disable welder
                self.control_welder(file, 0)

                # Move up at end
                self.add_linear_move(file, self.args.travel_speed, z=(z_pos + self.args.z_clearance))

                x_pos += x_gap_between_lines

                # Move above new start
                self.add_rapid_move(file, self.args.travel_speed, x_pos, y_pos)

                # Move down to start position
                self.add_linear_move(file, self.args.travel_speed, z=z_pos)

            z_pos += self.args.weld_layer_height
            # Move up to start position
            # TODO could optimize this small movement out
            self.add_linear_move(file, self.args.travel_speed, z=z_pos)

        # Disable welder Just in case
        self.control_welder(file, 0)

    # TODO add time estimate and min/max vals
    def write_config(self, file: TextIOWrapper):
        pass

    def control_welder(self, file: TextIOWrapper, status: int):
        if status != 1 and status != 0:
            raise ValueError(f"Unknown value set for welder value was {status}")
        file.write(f"{WELDER_CONTROL} S{status}\n")

    def add_linear_move(self, file: TextIOWrapper, speed: float, x: Optional[float] = None,
                        y: Optional[float] = None, z: Optional[float] = None):
        if x is not None:
            file.write(f"{LINEAR_MOVE} X{x} F{speed}\n")
        elif y is not None:
            file.write(f"{LINEAR_MOVE} Y{y} F{speed}\n")
        elif z is not None:
            file.write(f"{LINEAR_MOVE} Z{z} F{speed}\n")
        else:
            raise ValueError("No Distance given.")

    def add_rapid_move(self, file: TextIOWrapper, speed: float, x: Optional[float] = None,
                       y: Optional[float] = None, z: Optional[float] = None):

        cmd = MOVE
        if x is None and y is None and z is None:
            raise ValueError("No distance given")

        if x is not None:
            cmd += f" X{x}"

        if y is not None:
            cmd += f" Y{y}"

        if z is not None:
            cmd += f" Z{z}"

        cmd += f" F{speed}\n"

        file.write(cmd)

    def add_sleep(self, file: TextIOWrapper,
                  milliseconds: Optional[float] = None, seconds: Optional[int] = None):
        cmd = SLEEP_START
        if milliseconds is None and seconds is None:
            raise ValueError("No time given.")

        if milliseconds is not None:
            cmd += f" P{milliseconds}"

        if seconds is not None:
            cmd += f" S{seconds}"

        cmd += "\n"
        file.write(cmd)


if __name__ == "__main__":
    gen = GCODEGenerator()
    duet = DuetWebAPI("http://169.254.1.1")
    duet.connect()
    with open(os.path.join(DIR, gen.filename), "r") as f:
        duet.upload_file(f, gen.filename)
    duet.disconnect()
