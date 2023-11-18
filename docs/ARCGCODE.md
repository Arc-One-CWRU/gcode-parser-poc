# `arcgcode` <!-- omit in toc -->

`arcgcode` is a Python library designed for post-processing G-Codes for Wire Arc Additive Manufacturing (WAAM) machines. The library provides reusable components that you can use to build your own custom pipelines quickly.

## Table of Contents <!-- omit in toc -->

- [Concepts Overview](#concepts-overview)
- [Cura G-Code Sections](#cura-g-code-sections)
  - [Top Comment Section](#top-comment-section)
  - [Startup Script Section](#startup-script-section)
  - [G-Code Movements Section](#g-code-movements-section)
  - [End Script Section](#end-script-section)
  - [Bottom Comment Section](#bottom-comment-section)
- [Create Your Own `CuraGCodePipeline`](#create-your-own-curagcodepipeline)
  - [Implementing a Custom Section Processor](#implementing-a-custom-section-processor)
  - [Implementing a Custom Command Processor](#implementing-a-custom-command-processor)
  - [Integrate New Custom Processors](#integrate-new-custom-processors)
- [UltiMaker Cura Integration](#ultimaker-cura-integration)
  - [Cura `PostProcessingPlugin`](#cura-postprocessingplugin)
  - [Importing `arcgcode` into a Cura Post-Processing Script](#importing-arcgcode-into-a-cura-post-processing-script)

## Concepts Overview

The goal of the components in this repository is to take a G-Code file as input, do some sort of pre-defined modular transforms on the G-Code, and produce an output G-Code that works with a WAAM machine.

The key building blocks to make that possible are:

1. `SectionProcessorInterface`: Takes in one of the five pre-defined sections of a G-Code and processes it by returning a list of G-Code commands.
2. `CommandProcessorInterface`: Takes in a G-Code command and returns a resulting transformed command.
3. `CuraGCodePipeline`: Splits the input G-Code file into different sections and runs both the `SectionProcessorInterface` classes and the `CommandProcessorInterface` classes in succession.

A key aspect of any class that implements a processor interface is that they should be order-independent, which means that the order in-which it is specified in `CuraGCodePipeline` should not matter. This means that classes that implement `SectionProcessorInterface` **for the same section** should be produce the same outputs regardless of the order they were specified in.

You can see the general workflow below:

![](images/curagcodepipeline_overview.png)

**Figure 1. Overview of the processors executed in `CuraGCodePipeline.process`**

## Cura G-Code Sections

As you can see in **Figure 1**, there are multiple different types of section processors. Each of these sections is represented the `GCodeSection` enum, which looks like:

```python
class GCodeSection(str, Enum):
    TOP_COMMENT_SECTION = "TOP_COMMENT"
    STARTUP_SCRIPT_SECTION = "STARTUP_SCRIPT"
    GCODE_MOVEMENTS_SECTION = "GCODE_MOVEMENTS"
    END_SCRIPT_SECTION = "END_SCRIPT"
    BOTTOM_COMMENT = "BOTTOM_COMMENT"
```

All sections in `GCodeSection` are in **chronological order** from top to bottom. This means that a G-Code is structured as:

1. A top comment
2. A startup script
3. G-Code movements
4. An end script
5. A bottom comment

In the following documentation, we will describe what each section looks like and how we split the sections up in G-Codes in a general manner.

### Top Comment Section

The `TOP_COMMENT_SECTION` represents the top comment section in a Cura G-Code file. All comments in G-Code files start with a `;` character. An example of a `TOP_COMMENT_SECTION` is:

```
;FLAVOR:Marlin
;TIME:66
;Filament used: 0.00563198m
;Layer height: 1
;MINX:312.526
;MINY:120
;MINZ:0.3
;MAXX:342.474
;MAXY:120
;MAXZ:0.3
;Exported with Cura-DuetRRF v1.2.9 plugin by Thomas Kriechbaumer
....
; thumbnail_QOI end
;Generated with Cura_SteamEngine 5.3.0
```

A `TOP_COMMENT_SECTION` typically ends with a comment that starts with `;Generated with` (`END_OF_TOP_METADATA`) and we use that as the criteria for when it should be sliced.

### Startup Script Section

The `STARTUP_SCRIPT_SECTION` occurs right after the `TOP_COMMENT_SECTION`. It represents the start up script for the 3D printer or WAAM machine, which typically consists of sanity checks and calibration.

For instance, this may look like:

```
M105
M109 S0
M82 ;absolute extrusion mode
G28 ;Home
;G1 Z15.0 F6000 ;Move the platform down 15mm
;Prime the extruder
;G92 E0
;G1 F200 E3
;G92 E0
;M42 P1 S1
G92 E0
G92 E0
;LAYER_COUNT:2
```

The end of the startup script is when the G-Code movements start running which is represented by `";LAYER_COUNT:"` (`END_OF_STARTUP_SCRIPT`).

### G-Code Movements Section

The `GCODE_MOVEMENTS_SECTION` represents the commands that run the actual printing (movements, sleep, wait until temperature, extruder control, etc.). This section is characterized by layers (represented by the `;LAYER` comment) and different types of layers. You can see the [`ExcludeMeshLayer`](../src/arcgcode//processor/section/exclude_mesh.py) section processor as an example of how a layer type can be detected and manipulated.

A very simple example of a `GCODE_MOVEMENTS_SECTION` looks like:

```
;LAYER_COUNT:2
;LAYER:0
M107
;MESH:WeldingLineTest.STL
G0 F600 X342.474 Y120 Z0.3
;TYPE:WALL-OUTER
G1 F60 X312.526 Y120 E5.63198
;TIME_ELAPSED:66.230551
```

A `GCODE_MOVEMENTS_SECTION` ends when the `;TIME_ELAPSED` (`END_OF_GCODE_MOVEMENTS`) shows up.

### End Script Section

Just like how each G-Code has a startup script, each one has an end script, which consists of cleanup and sanity checks like turning the extruder off. The end script occurs **right after** the G-Code movements are done.

An example `END_SCRIPT_SECTION` looks like:

```
;M104 S0
;M140 S0
;Retract the filament
;G92 E1
;G1 E-1 F300
;G28 X0 Y0
;M84
M42 P1 S0
G4 S5
G28
M82 ;absolute extrusion mode
;End of Gcode
```

The end script ends when the comment `;End of Gcode` (`END_OF_GCODE`) is specified.

### Bottom Comment Section

The `BOTTOM_COMMENT` is whatever is left **after** the end script, which is typically a comment, such as:

```
;SETTING_3 {"global_quality": "[general]\\nversion = 4\\nname = Arc One #2\\ndef
;SETTING_3 inition = custom\\n\\n[metadata]\\ntype = quality_changes\\nquality_t
;SETTING_3 ype = extra coarse\\nsetting_version = 21\\n\\n[values]\\nadhesion_ty
;SETTING_3 pe = none\\nlayer_height = 1\\n\\n", "extruder_quality": ["[general]\
;SETTING_3 \nversion = 4\\nname = Arc One #2\\ndefinition = custom\\n\\n[metadat
;SETTING_3 a]\\ntype = quality_changes\\nquality_type = extra coarse\\nintent_ca
;SETTING_3 tegory = default\\nposition = 0\\nsetting_version = 21\\n\\n[values]\
;SETTING_3 \ncool_fan_enabled = False\\nmaterial_print_temperature = 0\\nretract
;SETTING_3 ion_enable = False\\nspeed_print = 2\\nspeed_travel = 20\\nwall_thick
;SETTING_3 ness = 1\\n\\n"]}
```

## Create Your Own `CuraGCodePipeline`

As previously mentioned, the `CuraGCodePipeline` is the core class that actually links the processors and runs the G-Code post-processing.

An example of how it is used is done in [`CuraPostProcessor`](../src/arcgcode/v1/postprocessor.py):

```python
        gcode_pipeline = CuraGCodePipeline(
            section_processors=[
                AddSleep(sleep_time=self.settings.sleep_time),
                RotateStartLayerPrint(self.settings.rotate_amount),
                AllWelderControl(), MoveUpZ(self.settings.weld_gap),
                AddMicerSettings(settings=self.settings),
            ],
            command_processor=[ExtruderRemover()])
        new_gcode = gcode_pipeline.process(data)
```

It takes in a G-Code file that is split into a list of strings and calls `CuraGCodePipeline.process` to generate the new G-Code. All of the classes specified for `section_processors` implement the `SectionProcessorInterface` interface and all of the classes specified for `command_processors` implement the `CommandProcessorInterface` interface.

By choosing to abstract the data processing in an interface with functions, the actual class initialization signature and class properties can vary depending on the desired operation, which makes the processors easy to create!

Likewise, you can easily customize your own pipeline by adding or removing section processors or command processors.

In the following sections, we will cover how to create your own custom processors and use them!

### Implementing a Custom Section Processor

All of the processors are classes that implement either `SectionProcessorInterface` or `CommandProcessorInterface`.

To implement `SectionProcessorInterface`, you need to create a class that has the methods `process(self, gcode_section: list[str]) -> list[str]` and `section_type(self) -> GCodeSection`. A minimal section processor for the G-Code Movements Section would look like:

```python
class HelloWorldSectionProcessor(SectionProcessorInterface):
    """Prints Hello World while processing :)
    """

    def __init__(self) -> None:
        super().__init__()

    def process(self, gcode_section: list[str]) -> list[str]:
        """Prints Hello World while processing :)
        """
        print("Hello World!")
        # TODO: Normally you would just iterate through the
        # gcode_section and create a new list of G-Code command
        # strings. The resulting list of strings DOES NOT
        # need to be the same length as the input.
        return gcode_section

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION
```

A realistic example of a section processor used by the Arc Research team as of 10/21 is `AddMicerSettings`.

```python
class AddMicerSettings(SectionProcessorInterface):
    """Adds the micer settings to GCode file.
    """

    def __init__(self, settings: CuraMicerSettings) -> None:
        super().__init__()
        self.settings = settings

    def process(self, gcode_section: list[str]) -> list[str]:
        """Reads the G-Code file buffer and does an action. It should return
        the desired G-Code string for that section.
        """
        new_gcode_section: list[str] = []
        for instruction in gcode_section:
            GENERATED_STRING = ";Generated with Cura_SteamEngine 5.4.0"
            if instruction.startswith(GENERATED_STRING):
                new_gcode_section.append(f"{GENERATED_STRING} + Micer\n")
            elif instruction.startswith(";MAXZ:"):
                new_gcode_section.append(instruction + "\n;Micer Settings\n")
                # Iterate over the attributes of the dataclass
                for field in fields(self.settings):
                    settings_attr = field.name
                    settings_val = getattr(self.settings, settings_attr)
                    parsed_settings = f';{settings_attr} = {settings_val}\n'
                    new_gcode_section.append(parsed_settings)
            else:
                new_gcode_section.append(instruction)

        return new_gcode_section

    def section_type(self) -> GCodeSection:
        """Returns the current section type.
        """
        return GCodeSection.GCODE_MOVEMENTS_SECTION
```

As you can see, `AddMicerSettings` just implements the two required methods. Anything else including the `__init__` function signature is flexible.

### Implementing a Custom Command Processor

`CommandProcessorInterface` is a bit simpler. To implement this interface, create a class that has the `process(self, gcode_instruction: str) -> str` method. A minimal command processor would look like:

```python
class HelloWorldCommandProcessor(CommandProcessorInterface):
    def __init__(self) -> None:
        super().__init__()

    def process(self, gcode_instruction: str) -> str:
        """Prints Hello World when processing each G-Code command!
        """
        print("Hello World!")
        # TODO: Do some manipulation with the gcode_instruction
        # which could look like G1 E..., or G92 E0, etc.
        return gcode_instruction
```

An example we currently use is `ExtruderRemover`:

```python
class ExtruderRemover(CommandProcessorInterface):
    """Removes the extruder argument in commands that have Xnnn, Ynnn, Znnn,
    Ennn as arguments.

    These commands include but are not limited to:
    G0, G1, G2, G3, G92, M566
    """

    def __init__(self) -> None:
        super().__init__()
        self.extruder_g1_matcher = re.compile(
            r"([E][-+]?([0-9]*\.[0-9]*|[0-9]*))\w+")

    def should_skip(self, gcode_instruction: str) -> bool:
        """Checks if the given G-Code instruction should be skipped.

        Args:
            gcode_instruction (str): The G-Code instruction to check.

        Returns:
            bool: True if the instruction should be skipped.
        """

        skip_line = "X" not in gcode_instruction and \
            "Y" not in gcode_instruction and \
            "Z" not in gcode_instruction and " E" in gcode_instruction

        return skip_line

    def process(self, gcode_instruction: str) -> str:
        """Matches a G-Code instruction. It should return
        the desired G-Code string for that line.
        """
        if self.should_skip(gcode_instruction):
            return gcode_instruction

        # Remove all extruder instructions in G1 commands
        new_g1 = self.extruder_g1_matcher.sub("", gcode_instruction)
        return new_g1
```

In the above example, `ExtruderRemover.should_skip` is not required to implement the `CommandProcessorInterface`, but it serves as a useful utility function to abstract some of the logic for `ExtruderRemover.process`.

### Integrate New Custom Processors

Once you've created a custom processor (either a section or command processor), simply add it to the list in [`CuraPostProcessor`](../src/arcgcode/v1/postprocessor.py)'s `CuraGCodePipeline` initialization:

```python
        gcode_pipeline = CuraGCodePipeline(
            section_processors=[
                # INSERT HERE:
                HelloWorldSectionProcessor(),
                AddSleep(sleep_time=self.settings.sleep_time),
                RotateStartLayerPrint(self.settings.rotate_amount),
                AllWelderControl(), MoveUpZ(self.settings.weld_gap),
                AddMicerSettings(settings=self.settings),
            ],
            command_processor=[
                # OR HERE
                HelloWorldCommandProcessor(),
                ExtruderRemover()
            ])
        new_gcode = gcode_pipeline.process(data)
```

## UltiMaker Cura Integration

This section covers the deep-dive on how we actually integrate `arcgcode` into UltiMaker Cura.

### Cura `PostProcessingPlugin`

The Cura [`PostProcessingPlugin`](https://github.com/Ultimaker/Cura/tree/main/plugins/PostProcessingPlugin) is Cura's official way to allow you to use custom Python scripts to post-process a Cura G-Code.

The `PostProcessingPlugin` reads those Python scripts from the configuration scripts directory. For example, on Linux, that directory is `~/.local/share/cura/5.3/scripts`.

> You can get the Cura scripts directory through `Cura > Help > Show configuration folder`. It will open up the configuration folder and you should copy the path to the `scripts` directory as the argument for `install.py`. Afterwards, just open up Cura and go to `Extensions > Post Processing > Modify G-Code > Add Script` and you should see your post-processing script if it is valid!

Examples of post-processing scripts we have for Arc Research are in the [`plugins` directory](../plugins/). These are the actual scripts that we use for the Arc One WAAM machine!

To actually print with the plugin, make sure that the you've added the scripts with the parameters you want to test. These paramters are empirically optimized based on trial and error (looking at which parameters produce the best quality prints).

Afterwards, slice the STL model with the script active and upload it to the WAAM machine (the Duet3D). Please refer to the standard operating procedure. Please ask an Arc Research team member for access to that document.

### Importing `arcgcode` into a Cura Post-Processing Script

In normal Python, you would install `arcgcode` through `pip3 install -r requirements.txt && pip3 install -e .`. Then would would simply import it with something like `import arcgcode`.

However, that workflow does not work for a Cura post-processing script because UltiMaker Cura has its own built-in Python executable! That means that it does **not** use the same Python executable and packages as the one you have installed on your system or virtual environment! Therefore, if you installed `arcgcode` with `pip3`, it would only install it for your local Python installation, not the Cura one.

We circumvented this issue by essentially adding the `arcgcode` package path to the Cura Python's `sys.path`. In Python, `sys.path` is a list of paths to directories that contain Python packages. Therefore, by adding the path to this repository + "src" to `sys.path` in a Cura post-processing script, we're able to `import arcgcode` successfully!

For example, in [`plugins/Micer.py`](../plugins/Micer.py), we call:

```python
import sys
try:
    import os
    import pathlib

    # Assumes that the Micer is in the same directory as the repository
    sys.path.append(os.path.abspath(os.path.join(pathlib.Path(__file__).parent,
                                                 "./src")))
    from arcgcode import v1
...
```

`sys.path.append(os.path.abspath(os.path.join(pathlib.Path(__file__).parent,"./src")))` looks like magic, but in essence, all it does is:

1. Look for the path to the plugins file (i.e. `~/.local/share/cura/5.3/scripts/Micer.py`)
2. Get the parent directory (`~/.local/share/cura/5.3/scripts`)
3. Add the absolute path of that parent directory + "src" to the `sys.path` (i.e. Add `~/.local/share/cura/5.3/scripts/src` to the `sys.path`)
   1. **Note:** `src` refers to the same `src` that contains the `arcgcode` folder in this repository!

This lets Cura's Python discover the `arcgcode` package in `src` and import it properly to utilize all of the utilities in `arcgcode`!

However, a downside with this approach is that everytime you want to make a change, you would need to re-run the `install.py` script as described in the official [README.md](../README.md).
