# Arc One GCode Parser <!-- omit in toc -->

GCode Parser for the Arc One WAAM 3D Printer.

## Table of Contents <!-- omit in toc -->

- [Getting Started](#getting-started)
- [Setting Up the Cura Plugin](#setting-up-the-cura-plugin)

## Getting Started

Make sure that you have Python 3 installed (at least Python 3.8).

```bash
# Make sure you are in the correct virtual env (if applicable)!
pip3 install -r requirements.txt
```

## Setting Up the Cura Plugin

For Linux, the path to your Cura scripts directory will look like:

```bash
$HOME/.config/cura/5.3/scripts/

# Don't use the path below EVEN if it looks right:
# (For some reason it doesn't work)
$HOME/.local/share/cura/5.3/plugins/PostProcessingPlugin/scripts
```

On Windows, the path will look like:

```bash
C:/Program Files/UltiMaker Cura 5.4.0/share/cura/plugins/PostProcessingPlugin/scripts/Micer.py
```
