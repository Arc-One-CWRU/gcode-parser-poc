# gcode-parser-poc

GCode Parser for the WAAM 3D Printer Proof of Concept

## Getting Started

Make sure that you have Python 3 installed (at least Python 3.8).

```bash
# Make sure you are in the correct virtual env (if applicable)!
pip3 install -r requirements.txt
```

You can find a full list of options with:

```bash
python3 main.py --help
```

An example command is:

```bash
# This will generate the parsed files in the current directory and print debug logging
python3 main.py -i "./examples" -o "./" -v
```

To use the updated framework CLI:

```bash
# This will generate the parsed files in the current directory and print debug logging
python3 framework_cli.py -i "./examples/line_welding_test.gcode" -o "./examples/generated" -v
```

To run the slicer:

```bash
# Linux
MESA_LOADER_DRIVER_OVERRIDE=i965 python3 app.py
```

## Setting Up the Cura Plugin

For Linux, the path to your Cura scripts directory will look like:

```bash
$HOME/.config/cura/5.3/scripts/

# Don't use this path:
# (For some reason it doesn't work)
$HOME/.local/share/cura/5.3/plugins/PostProcessingPlugin/scripts
```

On Windows, the path will look like:

```bash
C:/Program Files/UltiMaker Cura 5.4.0/share/cura/plugins/PostProcessingPlugin/scripts/Micer.py
```

## Misc Notes

- Cleanup repo & update requirements.txt
- Unit test
  - non-destructive
- More complex shapes
  - If shape is too small, no go
- make sure to always do a dry run
- Need plugin to upload gcode
  - need to plug in ethernet, just use the arc one computer to print stuff
- Replace sleep with GCode command for wait to temperature
- pylint
