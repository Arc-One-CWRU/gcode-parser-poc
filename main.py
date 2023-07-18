# Parses GCode files based on the instructions in ./examples/README.md
if __name__ == "__main__":
    import argparse
    import logging
    import os
    import sys
    from glob import glob

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

    if not os.path.isdir(args.output_dir):
        logging.error(
            "specified ouput dir '%s' is not a directory", args.output_dir)

    input_dir = os.path.abspath(args.input_dir)
    output_dir = os.path.abspath(args.output_dir)

    gcodeFiles = glob(os.path.join(input_dir, "*.gcode"))
    if len(gcodeFiles) == 0:
        logging.error(
            "Found 0 GCode files in the specified input directory %s.\nPlease double check that it's specified correctly with -v", input_dir)
        sys.exit()

    logging.info("Found %d gcode files in input directory %s.\nConverting to WAAM version...", len(
        gcodeFiles), input_dir)

    for fname in gcodeFiles:
        with open(fname, "r", encoding="utf-8") as f:
            lines = f.readlines()
            logging.debug(lines)

    logging.info("Done! All created files are in %s", output_dir)
