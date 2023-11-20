# Arc One GCode Parser <!-- omit in toc -->

GCode Parser for the Arc One WAAM 3D Printer.

You can find the `arcgcode` framework developer documentation in [here](./docs/ARCGCODE.md).

## Table of Contents <!-- omit in toc -->

- [Getting Started](#getting-started)
- [Contributor's Getting Started](#contributors-getting-started)
- [Debugging with the CLI](#debugging-with-the-cli)
- [Timing with the CLI](#timing-with-the-cli)

## Getting Started

To install the Cura scripts, run `install.py` with a path to the Cura scripts directory:

```bash
# Linux
python3 install.py ~/.local/share/cura/5.3/scripts

# Windows
# In Administrator Command Prompt, cd into this repository.
cd C:\Users\Arc One\gcode-parser-poc
python install.py "C:\\Users\\Arc One\\AppData\\Roaming\\cura\\5.4\\scripts"
# TODO:
```

You can get the Cura scripts directory through `Cura > Help > Show configuration folder`. It will open up the configuration folder and you should copy the path to the `scripts` directory as the argument for `install.py`.

Afterwards, just open up Cura and go to `Extensions > Post Processing > Modify G-Code > Add Script > Micer`. Afterwards, feel free to slice and print!

## Contributor's Getting Started

Make sure that you have Python 3 installed (at least Python 3.8).

```bash
# Make sure you are in the correct virtual env (if applicable)!
pip3 install -r requirements.txt

pip install -e .
```

To deploy new changes, simply re-run the `install.py` script for your respective OS!

Likewise, to debug your changes, run:

```bash
# Linux
make -f Makefile.unix debug

# Windows
# TODO
```

## Debugging with the CLI

You can also debug the G-Code parsing with default settings with the CLI:

```bash
python cli.py gcode -i tests/gcodes/inputs/calibration_cube.gcode -o arc1_gcodes -v
```

This is much faster than slicing and then downloading the parsed G-Code in Cura to view your results.

## Timing with the CLI

To time your printing run with nice exporting, call:

```bash
python cli.py time
```
