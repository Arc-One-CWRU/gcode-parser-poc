# gcode-parser-poc

GCode Parser for the WAAM 3D Printer Proof of Concept

## Getting Started

Make sure that you have Python 3 installed (at least Python 3.8).

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
