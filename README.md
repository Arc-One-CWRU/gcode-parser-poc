# Arc One GCode Parser <!-- omit in toc -->

GCode Parser for the Arc One WAAM 3D Printer.

## Table of Contents <!-- omit in toc -->

- [Getting Started](#getting-started)
- [Setting Up the Cura Plugin](#setting-up-the-cura-plugin)
  - [Command for opening cura for Henry in windows](#command-for-opening-cura-for-henry-in-windows)

## Getting Started

Make sure that you have Python 3 installed (at least Python 3.8).

```bash
# Make sure you are in the correct virtual env (if applicable)!
pip3 install -r requirements.txt

pip install -e .
```

To run Cura with the plugin on Linux:

```bash
# Replace the paths with your own paths
make -f Makefile.unix prepare && make cura -f Makefile.unix GCODE_REPO_DIR=${HOME}/Coding/arc_one/gcode-parser-poc/src ULTIMAKER_EXE=${HOME}/Desktop/UltiMaker-Cura-5.3.1-linux-modern.AppImage
```

To run Cura with the plugin on Windows:

```bash
make -f Makefile.windows prepare && make cura -f Makefile.windows GCODE_REPO_DIR="C:\\Users\hwodz\\The Ultimate Vault\\Code\\gcode-parser-poc\\src" ULTIMAKER_EXE="C:\Program Files\UltiMaker Cura 5.4.0\UltiMaker-Cura.exe"
```

## Setting Up the Cura Plugin

For Linux, the path to your Cura scripts directory will look like:

```bash
$HOME/.config/cura/5.3/scripts/

# Don't use the path below EVEN if it looks right:
# (For some reason it doesn't work)
$HOME/.local/share/cura/5.3/plugins/PostProcessingPlugin/scripts

# Debugging
cat $HOME/.local/share/cura/5.3/cura.log | grep Error
```

On Windows, the path will look like:

```bash
C:/Program Files/UltiMaker Cura 5.4.0/share/cura/plugins/PostProcessingPlugin/scripts/Micer.py
```

### Command for opening cura for Henry in windows

```
setx GCODE_REPO_DIR "C:\\Users\hwodz\\The Ultimate Vault\\Code\\gcode-parser-poc\\src" && "C:\Program Files\UltiMaker Cura 5.4.0\UltiMaker-Cura.exe"
```
