import typer
from arcgcode.duet.timer import DuetTimer, ARC_ONE_DUET_URL
from typing_extensions import Annotated


app = typer.Typer()


@app.command()
def time():
    duet_timer = DuetTimer(ARC_ONE_DUET_URL)
    duet_timer.run()


# This is jank, but it makes things more readable
args_help = {
    "-i": "The path to an input directory of GCodes or the path to a G-Code " +
    "file to transform.",
    "-o": "The path to the output directory where the parsed GCodes will be " +
    "generated to",
    "-v": "Toggles on debug logging.",
}

# Type aliases for the gcode command.
InputDirOrFilePathCliArg = Annotated[str, typer.Option("--input", "-i",
                                                       help=args_help["-i"])]
OutputDirCliArg = Annotated[str, typer.Option("--output_dir", "-o",
                                              help=args_help["-o"])]
VerboseCliArg = Annotated[bool, typer.Option("--verbose", "-v",
                                             help=args_help["-v"])]


@app.command()
def gcode(input_dir_or_file_path: InputDirOrFilePathCliArg,
          output_dir: OutputDirCliArg,
          verbose: VerboseCliArg = True):
    """
    Processes the G-Code to a WAAM compatible format.

    This is a good backup just in-case the Cura post-processing script is not
    completely functional.

    You can generate a G-Code using Cura. Then call this command:

    python cli.py gcode -i PATH_TO_CURA_GCODE -o output_gcodes -v

    Make sure to replace PATH_TO_CURA_GCODE with the path to your generated
    Cura G-Code. This will generate the WAAM compatible G-Code inside of the
    output_gcodes directory relative to the current directory.

    An example that works as of 11/19 is:

    python cli.py gcode -i tests/gcodes/inputs/calibration_cube.gcode \
        -o arc1_gcodes -v

    This will generate a file called edited_calibration_cube.gcode in the
    arc1_gcodes directory. This new G-Code file should be compatible with the
    Arc One WAAM machine.
    """
    import logging
    import os
    import sys
    from glob import glob
    from pathlib import Path
    from arcgcode.v1 import CuraPostProcessor, CuraMicerSettings

    if (verbose):
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    logging.debug("args: Input Path: %s, Output Path: %s, Verbose: %r",
                  input_dir_or_file_path, output_dir, verbose)

    if (not os.path.isdir(input_dir_or_file_path) and
       not os.path.isfile(input_dir_or_file_path)):
        logging.error("specified input dir '%s' is not a directory or file",
                      input_dir_or_file_path)
        sys.exit()

    # Allows you to specify a non-existing output directory if necessary
    if not os.path.isdir(output_dir):
        output_dir_path = os.path.abspath(output_dir)
        logging.info("Creating output directory %s...", output_dir_path)
        os.makedirs(output_dir)

    if os.path.isfile(input_dir_or_file_path):
        gcode_files = [input_dir_or_file_path]
    else:
        input_dir = os.path.abspath(input_dir_or_file_path)
        gcode_files = glob(os.path.join(input_dir, "*.gcode"))

    if len(gcode_files) == 0:
        logging.error(
            "Found 0 GCode files in the specified input directory %s.\n" +
            "Please double check that it's specified correctly with -v",
            input_dir_or_file_path)
        sys.exit()

    output_dir = os.path.abspath(output_dir)

    logging.info("Found %d gcode files.\nConverting to WAAM version...", len(
        gcode_files))

    gcode_pipeline = CuraPostProcessor(CuraMicerSettings(weld_gap=8,
                                                         sleep_time=30,
                                                         rotate_amount=6,
                                                         movement_rate=0))
    for fname in gcode_files:
        with open(fname, "r", encoding="utf-8") as f:
            new_gcode = gcode_pipeline.execute(f.readlines())
            base_fname = f"edited_{Path(fname).name}"
            with open(os.path.join(output_dir, base_fname), "w",
                      encoding="utf-8") as f:
                f.write("".join(new_gcode))

    logging.info("Done! All created files are in %s", output_dir)
    return


if __name__ == "__main__":
    app()
