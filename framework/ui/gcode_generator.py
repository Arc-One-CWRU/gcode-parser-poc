# TODO move out of ui?

import os
from argparse import ArgumentParser
from datetime import datetime
from io import TextIOWrapper
from typing import Optional
from math import ceil, dist
from duetwebapi import DuetWebAPI
from requests.exceptions import ConnectionError
from enum import IntEnum

MOVE = "G0"
LINEAR_MOVE = "G1"
HOME = "G28 ;Homes\n"

SLEEP_START = "G4"

WELDER_CONTROL = "M42 P1"

DIR = "generated"
URL = "http://169.254.1.1"


class InfillType(IntEnum):
    STRAIGHT_LINES = 0
    SQUARES = 1
    SERPENTINE = 2


class GCODEGenerator:

    def __init__(self) -> None:
        # In seconds
        self.sleep_time: float = 0
        # In Minutes
        self.move_time: float = 0
        self.welding_time: float = 0
        self.curr_x = 0
        self.curr_y = 0
        self.curr_z = 0
        self.welding = False

        parser = ArgumentParser()
        parser.add_argument("-w", "--weld_gap", help="Weld gap distance (mm).",
                            type=float, default=8)
        parser.add_argument("-wh", "--weld_layer_height", help="Weld height distance (mm).",
                            type=float, default=1.6)
        parser.add_argument("-ww", "--weld_layer_width", help="Weld width distance (mm).",
                            type=float, default=8.5)

        parser.add_argument("-wlo", "--weld_layer_overlap", help="Overlap between weld lines (mm).",
                            type=float, default=6.1)

        parser.add_argument("-ts", "--travel_speed", help="Set transport speed (mm/min).",
                            type=float, default=1500)
        parser.add_argument("-ps", "--print_speed", help="Set print speed (mm/min).",
                            type=float, default=381)

        # Overall Dimensions of bed
        parser.add_argument("-xbs", "--x_bed_size", help="Set x bed size (mm).",
                            type=float, default=240)
        parser.add_argument("-ybs", "--y_bed_size", help="Set y bed size (mm).",
                            type=float, default=580)
        parser.add_argument("-zbs", "--z_bed_size", help="Set z bed size (mm).",
                            type=float, default=110)

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
                            type=float, default=90)

        # Print Type
        parser.add_argument("-i", "--infill_type", help="Specify infill type. 0 is for straight lines, 1 is for concentric squares and 2 is for lines snaking back and forth",
                            type=int, default=0)

        parser.add_argument("-al", "--alternate_layers", help="Want to alternate layers to avoid drooping?",
                            type=bool, default=True)

        parser.add_argument("-v", "--verbose", help="Debug logging.",
                            type=bool, default=False)

        self.args = parser.parse_args()

    # TODO this hurts me
    def set_x(self, x: float):
        self.args.x_size = x

    def set_y(self, y: float):
        self.args.y_size = y

    def set_z(self, z: float):
        self.args.z_size = z

    def set_x_corner(self, x_corner: float):
        self.args.x_corner = x_corner

    def set_y_corner(self, y_corner: float):
        self.args.y_corner = y_corner

    def set_infill_type(self, infill_type: InfillType):
        self.args.infill_type = infill_type.value

    def set_weld_gap(self, value: float):
        self.args.weld_gap = value

    def set_weld_layer_height(self, value: float):
        self.args.weld_layer_height = value

    def set_weld_layer_width(self, value: float):
        self.args.weld_layer_width = value

    def set_weld_layer_overlap(self, value: float):
        self.args.weld_layer_overlap = value

    def set_travel_speed(self, value: float):
        self.args.travel_speed = value

    def set_print_speed(self, value: float):
        self.args.print_speed = value

    def set_x_bed_size(self, value: float):
        self.args.x_bed_size = value

    def set_y_bed_size(self, value: float):
        self.args.y_bed_size = value

    def set_z_bed_size(self, value: float):
        self.args.z_bed_size = value

    def set_z_clearance(self, value: float):
        self.args.z_clearance = value

    def set_alternate_layers(self, value: bool):
        self.args.alternate_layers = value

    def safety_checks(self):
        # Parameter not set
        for kwarg in self.args._get_kwargs():
            if kwarg[1] is None:
                raise ValueError(f"{kwarg[0]} is None")

        if self.args.x_size > self.args.x_bed_size or self.args.x_corner > self.args.x_bed_size:
            raise ValueError("X dimension does not fit in bed")

        if self.args.y_size > self.args.y_bed_size or self.args.y_corner > self.args.y_bed_size:
            raise ValueError("Y dimension does not fit in bed")

        if self.args.z_size + self.args.z_clearance > self.args.z_bed_size:
            raise ValueError("Z dimension does not fit in bed")

    def run(self):
        self.filename = f"{str(datetime.now())[:-7]}.gcode".replace(" ", " Time=").replace(":", " ")
        self.safety_checks()
        with open(os.path.join(DIR, self.filename), "x") as f:
            print("Started Generating Gcode File")
            self.write_info(f)
            self.write_volume(f)

        self.write_config()
        print("Finished Generating Gcode File.")

    def write_info(self, file: TextIOWrapper):
        file.write(";Print Information\n")
        file.write(f";Weld Gap = {self.args.weld_gap} mm\n")
        file.write(f";Weld Height = {self.args.weld_layer_height} mm\n")
        file.write(f";Weld Width = {self.args.weld_layer_width} mm\n")
        file.write(f";Weld Layer Overlap = {self.args.weld_layer_overlap} mm\n")
        file.write(f";Transport Speed = {self.args.travel_speed} mm/min\n")
        file.write(f";Print Speed = {self.args.print_speed} mm/min\n")
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
        file.write(f";Alternate Layer direction? = {self.args.alternate_layers}\n")
        file.write(f";Infill Type = {InfillType(self.args.infill_type).name}\n")

    # TODO add different directions around the rect
    # TODO add the ability to start in the middle of an edge of the rectangle
    def write_rect(self, file: TextIOWrapper, x1: float, y1: float, x2: float, y2: float):
        self.control_welder(file, 1)
        self.add_linear_move(file, self.args.weld_speed, x2)
        self.add_linear_move(file, self.args.weld_speed, y2)
        self.add_linear_move(file, self.args.weld_speed, x1)
        self.add_linear_move(file, self.args.weld_speed, y1)
        self.control_welder(file, 0)

    def write_serpentine(self, file: TextIOWrapper):
        pass

    def write_serpentine_with_box(self, file: TextIOWrapper):
        self.z_line_count: int = ceil(self.args.z_size / self.args.weld_layer_height)

        x_pos = self.args.x_corner
        y_pos = self.args.y_corner
        z_pos = self.args.weld_gap

        for i in range(self.z_line_count):
            self.write_rect(file, x_pos, y_pos,
                            x_pos + self.args.x_size,
                            y_pos + self.args.x_size)







            z_pos += self.args.weld_layer_height

            if i != (self.z_line_count - 1):
                # Wait for cool
                self.add_sleep(file, seconds=15)

                # Move above to start position
                self.add_rapid_move(file, self.args.travel_speed, x_pos, y_pos,
                                    (z_pos + self.args.z_clearance))

                # Move Down to new corner
                self.add_linear_move(file, self.args.travel_speed, z=z_pos)

    def write_squares(self, file: TextIOWrapper):
        raise NotImplementedError

    def write_straight_lines(self, file: TextIOWrapper):
        self.z_line_count: int = ceil(self.args.z_size / self.args.weld_layer_height)
        self.y_line_count: int = ceil((self.args.y_size - self.args.weld_layer_width) / self.args.weld_layer_overlap) + 1

        x_pos = self.args.x_corner
        y_pos = self.args.y_corner
        z_pos = self.args.weld_gap

        counter = 0
        flip = 1

        for i in range(self.z_line_count):
            for j in range(self.y_line_count):

                # Settle in
                self.add_sleep(file, seconds=1)

                # Enable welder
                self.control_welder(file, 1)

                # Moves a long line
                self.add_linear_move(file, self.args.print_speed, x=(x_pos + self.args.x_size * flip))

                # Disable welder
                self.control_welder(file, 0)

                # Move up at end
                self.add_linear_move(file, self.args.travel_speed, z=(z_pos + self.args.z_clearance))

                if j != (self.y_line_count - 1):

                    # Wait for cool
                    self.add_sleep(file, seconds=15)
                    y_pos += self.args.weld_layer_overlap

                    # Move above new start
                    self.add_rapid_move(file, self.args.travel_speed, x_pos, y_pos)

                    # Move down to start position
                    self.add_linear_move(file, self.args.travel_speed, z=z_pos)
                else:
                    # Reset Y corner and raise height
                    y_pos = self.args.y_corner
                    z_pos += self.args.weld_layer_height

                    # Used for alternating welding lines
                    x_pos = x_pos + self.args.x_size if counter % 2 == 0 and self.args.alternate_layers else self.args.x_corner
                    counter += 1
                    flip *= -1

            if i != (self.z_line_count - 1):
                # Wait for cool
                self.add_sleep(file, seconds=15)

                # Move above to start position
                self.add_rapid_move(file, self.args.travel_speed, x_pos, y_pos, (z_pos + self.args.z_clearance))

                # Move Down to new corner
                self.add_linear_move(file, self.args.travel_speed, z=z_pos)

    def write_volume(self, file: TextIOWrapper):
        # Move home
        file.write(HOME)

        # Raise to avoid junk on table
        self.add_linear_move(file, self.args.travel_speed, z=self.args.z_clearance)

        # Move above starting position
        self.add_rapid_move(file, self.args.travel_speed, self.args.x_corner, self.args.y_corner)

        # Move into starting position
        self.add_linear_move(file, self.args.travel_speed, z=self.args.weld_gap)

        match self.args.infill_type:
            case InfillType.STRAIGHT_LINES:
                self.write_straight_lines(file)
            case InfillType.SQUARES:
                self.write_squares(file)
            case InfillType.SERPENTINE:
                self.write_serpentine_with_box(file)
            case _:
                raise ValueError("Uknown Infill Type.")

        # Disable welder Just in case
        self.control_welder(file, 0)

    def write_config(self):
        with open(os.path.join(DIR, self.filename), "r+") as file:
            content = file.read()

            file.seek(0, 0)
            file.write(";FLAVOR:RepRap\n")
            file.write(f";TIME:{self.sleep_time + (self.move_time + self.welding_time)*60}\n")
            # Magic numbers is inches/min to mm/sec
            file.write(f";Filament used: {(self.welding_time*60) * 105.833}mm\n")
            file.write(f";Layer height: {self.args.weld_layer_height}\n")
            file.write(f";MINX:{self.args.x_corner}\n")
            file.write(f";MINY:{self.args.y_corner}\n")
            file.write(";MINZ:0\n")
            file.write(f";MAXX:{self.args.x_corner + self.args.x_size}\n")
            file.write(f";MAXY:{self.args.y_corner + self.args.y_size}\n")
            file.write(f";MAXZ:{self.args.z_clearance + self.args.z_size}\n")
            file.write(";Generated with Micer 0.0.5\n")
            # Custom Config
            file.write(f";Z Layers ={self.z_line_count}, Y Layers ={self.y_line_count}\n")
            print(f"Z Layers ={self.z_line_count}, Y Layers ={self.y_line_count}")
            file.write("\n\n")
            file.write(content)

    def control_welder(self, file: TextIOWrapper, status: int):
        if status != 1 and status != 0:
            raise ValueError(f"Unknown value set for welder value was {status}")

        self.welding = True if status == 1 else False
        file.write(f"{WELDER_CONTROL} S{status}\n")

    def add_linear_move(self, file: TextIOWrapper, speed: float,
                        x: Optional[float] = None,
                        y: Optional[float] = None,
                        z: Optional[float] = None):
        time = None

        if x is not None:
            file.write(f"{LINEAR_MOVE} X{x} F{speed}\n")
            time = abs(x-self.curr_x)/speed
            self.curr_x = x
        elif y is not None:
            file.write(f"{LINEAR_MOVE} Y{y} F{speed}\n")
            time = abs(y-self.curr_y)/speed
            self.curr_y = y
        elif z is not None:
            file.write(f"{LINEAR_MOVE} Z{z} F{speed}\n")
            time = abs(z-self.curr_z)/speed
            self.curr_z = z
        else:
            raise ValueError("No Distance given.")

        if self.welding:
            self.welding_time += time
        else:
            self.move_time += time

    def add_rapid_move(self, file: TextIOWrapper, speed: float,
                       x: Optional[float] = None,
                       y: Optional[float] = None,
                       z: Optional[float] = None):

        cmd = MOVE
        if x is None and y is None and z is None:
            raise ValueError("No distance given")

        if x is not None:
            cmd += f" X{x}"
        else:
            x = self.curr_x

        if y is not None:
            cmd += f" Y{y}"
        else:
            y = self.curr_y

        if z is not None:
            cmd += f" Z{z}"
        else:
            z = self.curr_z

        cmd += f" F{speed}\n"

        time = dist((x, y, z), (self.curr_x, self.curr_y, self.curr_z))/speed
        if self.welding:
            self.welding_time += time
        else:
            self.move_time += time

        file.write(cmd)

    def add_sleep(self, file: TextIOWrapper,
                  milliseconds: Optional[float] = None, seconds: Optional[int] = None):
        cmd = SLEEP_START
        if milliseconds is None and seconds is None:
            raise ValueError("No time given.")

        if milliseconds is not None:
            cmd += f" P{milliseconds}"
            self.sleep_time += milliseconds/1000

        if seconds is not None:
            cmd += f" S{seconds}"
            self.sleep_time += seconds

        cmd += "\n"
        file.write(cmd)

    def upload(self):
        duet = DuetWebAPI(URL)
        duet.connect()
        print("Connected to Duet")
        stuff = None
        while stuff is None:
            try:
                with open(os.path.join(DIR, self.filename), "r") as f:
                    file_str = f.read()
                    stuff = duet.upload_file(file_str.encode(), self.filename)
            except ConnectionError as e:
                print(e)

        print("Finished upload")
        duet.disconnect()


if __name__ == "__main__":
    gen = GCODEGenerator()
    gen.run()
    gen.upload()
