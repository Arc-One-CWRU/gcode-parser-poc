"""
Arc One GCode Parser Proof Of Concept
Parses GCode files based on the instructions in ./examples/README.md so that
our printer can print the GCode.
"""

if __name__ == "__main__":
    import argparse
    import logging
    import os
    import sys
    from glob import glob
    from pathlib import Path
    from arcgcode.v1 import CuraPostProcessor, CuraMicerSettings  

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input directory of GCodes or" +
                        "G-Code file to transform.",
                        type=str)
    parser.add_argument("-o", "--output_dir", help="Output directory where " +
                        "the parsed GCodes will go.", type=str)
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Debug logging.")
    args = parser.parse_args()

    if (args.verbose):
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    logging.debug("args: %s", args)

    if not os.path.isdir(args.input) and not os.path.isfile(args.input):
        logging.error(
            "specified input dir '%s' is not a directory or file", args.input)
        sys.exit()

    # Allows you to specify a non-existing output directory if necessary
    if not os.path.isdir(args.output_dir):
        output_dir_path = os.path.abspath(args.output_dir)
        logging.info("Creating output directory %s...", output_dir_path)
        os.makedirs(args.output_dir)

    if os.path.isfile(args.input):
        gcode_files = [args.input]
    else:
        input_dir = os.path.abspath(args.input)
        gcode_files = glob(os.path.join(input_dir, "*.gcode"))

    if len(gcode_files) == 0:
        logging.error(
            "Found 0 GCode files in the specified input directory %s.\n" +
            "Please double check that it's specified correctly with -v",
            args.input)
        sys.exit()

    output_dir = os.path.abspath(args.output_dir)

    logging.info("Found %d gcode files.\nConverting to WAAM version...", len(
        gcode_files))

    gcode_pipeline = CuraPostProcessor(CuraMicerSettings(weld_gap=8,
                                                         sleep_time=30,
                                                         rotate_amount=6))
    for fname in gcode_files:
        with open(fname, "r", encoding="utf-8") as f:
            new_gcode = gcode_pipeline.execute(f.readlines())
            base_fname = f"edited_{Path(fname).name}"
            with open(os.path.join(output_dir, base_fname), "w",
                      encoding="utf-8") as f:
                f.write("".join(new_gcode))

    logging.info("Done! All created files are in %s", output_dir)
