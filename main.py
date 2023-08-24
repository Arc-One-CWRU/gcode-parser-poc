"""
Arc One GCode Parser Proof Of Concept

Parses GCode files based on the instructions in ./examples/README.md so that
our printer can print the GCode.
"""
import io
import re

END_OF_GCODE = ";End of Gcode"
END_OF_TOP_METADATA = ";Generated with"


def read_top_metadata(file_buffer: io.TextIOWrapper) -> str:
    """Reads the top metadata comments.
    """
    is_metadata = True
    top_metadata = ""
    while is_metadata:
        curr_line = file_buffer.readline()
        top_metadata += curr_line
        if curr_line.startswith(END_OF_TOP_METADATA):
            is_metadata = False
    return top_metadata


def to_new_gcode(file_buffer: io.TextIOWrapper) -> str:
    """Reads GCode files line by line and parses them into the Arc-One printer
    format.

    Assumptions:
    * The input gcodes use G28 for homing.
    * The input gcodes turn off the extruder gun at some point.
    """
    has_reached_end = False
    new_file = ""
    top_metadata = read_top_metadata(file_buffer=file_buffer)

    new_file += top_metadata + "\n"

    # 1. Read until G28 is reached.
    # If there is no G28, throw an error.
    starts_with_g28 = False
    while (not starts_with_g28):
        curr_line = file_buffer.readline()
        has_reached_end = curr_line.startswith(END_OF_GCODE)
        if curr_line == "" or has_reached_end:
            raise Exception("G28 must be specified in the gcode.")

        if curr_line.startswith("G28"):
            starts_with_g28 = True
            new_file += curr_line

    # 2. Raise the welding tip `G1 Z60 F6000` right after homing, move to the
    # starting point and lower the tip.
    # 3. Turn on the welder.
    setup_instructions = """G1 Z60 F6000; Raise the welding tip
G0 F600 X342.474 Y120; Move to the starting spot
G0 F6000 Z0.3; Lower the tip
M42 P1 S1; Turn on the welder
"""
    new_file += setup_instructions

    # 3. Copy over any non-blacklisted instructions until a G1 movement command
    blacklisted_commands = [
        "M107",  # Turns fan off (not needed right now)
        "G92",  # Sets current extruder position to 0
        "G0"
    ]

    extruder_g1_matcher = re.compile(r"([E][-+]?([0-9]*\.[0-9]*|[0-9]*))\w+")
    starts_with_g1 = False
    while (not starts_with_g1):
        curr_line = file_buffer.readline()
        has_reached_end = curr_line.startswith(END_OF_GCODE)
        if curr_line == "" or has_reached_end:
            raise Exception("no movement commands found in gcode")

        if curr_line.startswith("G1"):
            logging.debug("converting G1 instruction: %s", curr_line)
            # Remove all extruder instructions in G1 commands
            new_g1 = extruder_g1_matcher.sub("", curr_line)
            new_file += new_g1
            starts_with_g1 = True
        elif curr_line.startswith(";"):
            continue
        elif curr_line.split(" ")[0].strip() not in blacklisted_commands:
            new_file += curr_line

    # Move gun until there is an instruction to turn off the welder.
    turn_off = False
    while (not turn_off):
        curr_line = file_buffer.readline()
        has_reached_end = curr_line.startswith(END_OF_GCODE)
        if curr_line == "" or has_reached_end:
            # Must turn off the extruder even if it's not specified.
            new_file += "M42 P1 S0"
            logging.warning(
                "automatically adding the turn off extruder command to the output \
                 gcode even though not in input gcode")
        elif curr_line.startswith("G1"):
            logging.debug("converting G1 instruction: %s", curr_line)
            # Remove all extruder instructions in G1 commands
            new_g1 = extruder_g1_matcher.sub("", curr_line)
            new_file += new_g1
        elif curr_line.startswith("M42 P1 S0"):
            turn_off = True
            new_file += curr_line

    raise_tip_instruction = "G0 F20000 Z60; Raises the welding tip, quickly (F sets speed)"
    new_file += raise_tip_instruction

    # Ignore everything after turning off
    # Just read until the end of the gcode if applicable
    if not has_reached_end:
        while (not has_reached_end):
            curr_line = file_buffer.readline()
            has_reached_end = curr_line.startswith(END_OF_GCODE)

    # Append the rest of the GCode
    new_file += "\n\n" + END_OF_GCODE + "\n"
    new_file += "".join(file_buffer.readlines())

    return new_file


if __name__ == "__main__":
    import argparse
    import logging
    import os
    import sys
    from glob import glob
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_dir", help="Input directory of GCodes to transform.",
                        type=str)
    parser.add_argument("-o", "--output_dir", help="Output directory where the parsed GCodes will go.",
                        type=str)
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Debug logging.")
    args = parser.parse_args()

    if (args.verbose):
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    logging.debug("args: %s", args)

    if not os.path.isdir(args.input_dir):
        logging.error(
            "specified input dir '%s' is not a directory", args.input_dir)
        sys.exit()

    if not os.path.isdir(args.output_dir):
        logging.error(
            "specified ouput dir '%s' is not a directory", args.output_dir)
        sys.exit()

    input_dir = os.path.abspath(args.input_dir)
    output_dir = os.path.abspath(args.output_dir)

    gcode_files = glob(os.path.join(input_dir, "*.gcode"))
    if len(gcode_files) == 0:
        logging.error(
            "Found 0 GCode files in the specified input directory %s.\nPlease double check that it's specified correctly with -v", input_dir)
        sys.exit()

    logging.info("Found %d gcode files in input directory %s.\nConverting to WAAM version...", len(
        gcode_files), input_dir)

    for fname in gcode_files:
        with open(fname, "r", encoding="utf-8") as f:
            new_gcode = to_new_gcode(f)
            base_fname = f"edited_{Path(fname).name}"
            with open(os.path.join(output_dir, base_fname), "w", encoding="utf-8") as f:
                f.write(new_gcode)

    logging.info("Done! All created files are in %s", output_dir)
