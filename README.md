# Arc One GCode Parser <!-- omit in toc -->

GCode Parser for the Arc One WAAM 3D Printer.

## Table of Contents <!-- omit in toc -->

- [Getting Started](#getting-started)
- [Contributor's Getting Started](#contributors-getting-started)

## Getting Started

To install the Cura scripts, run `install.py` with a path to the Cura scripts directory:

```bash
# Linux
python3 install.py ~/.local/share/cura/5.3/scripts

# Windows
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
