# `arcgcode` <!-- omit in toc -->

`arcgcode` is a Python library designed for post-processing G-Codes for Wire Arc Additive Manufacturing (WAAM) machines. The library provides reusable components that you can use to build your own custom pipelines quickly.

## Table of Contents <!-- omit in toc -->

- [Concepts Overview](#concepts-overview)
- [Create Your Own `CuraGCodePipeline`](#create-your-own-curagcodepipeline)
  - [Implementing Custom Processors](#implementing-custom-processors)
  - [Integrate New Custom Processors](#integrate-new-custom-processors)

## Concepts Overview

The goal of the components in this repository is to take a G-Code file as input, do some sort of pre-defined modular transforms on the G-Code, and produce an output G-Code that works with a WAAM machine.

The key building blocks to make that possible are:

1. `SectionProcessorInterface`: Takes in one of the five pre-defined sections of a G-Code and processes it by returning a list of G-Code commands.
2. `CommandProcessorInterface`: Takes in a G-Code command and returns a resulting transformed command.
3. `CuraGCodePipeline`: Splits the input G-Code file into different sections and runs both the `SectionProcessorInterface` classes and the `CommandProcessorInterface` classes in succession.

A key aspect of any class that implements a processor interface is that they should be order-independent, which means that the order in-which it is specified in `CuraGCodePipeline` should not matter. This means that classes that implement `SectionProcessorInterface` for the G-Code movements section should be produce the same outputs regardless of the order they were specified in.

You can see the general workflow below:

![](images/curagcodepipeline_overview.png)

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

### Implementing Custom Processors

All of the processors are classes that implement either `SectionProcessorInterface` or `CommandProcessorInterface`.

To implement `SectionProcessorInterface`, you need to create a class that has the methods `process(self, gcode_section: list[str]) -> list[str]` and `section_type(self) -> GCodeSection`. A simple example of a section processor used by the Arc Research team as of 10/21 is `AddMicerSettings`.

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

`CommandProcessorInterface` is a bit simpler. To implement this interface, create a class that has the `process(self, gcode_instruction: str) -> str` method. For example, the command processor that we currently use for Arc Research is `ExtruderRemover`:

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

Once you've created a custom processor (either a section or command processor), simply add it to the list in `CuraPostProcessor`'s `CuraGCodePipeline` initialization:

```py
        gcode_pipeline = CuraGCodePipeline(
            section_processors=[
                # INSERT HERE:
                YourNewCuraSectionProcessor(),
                AddSleep(sleep_time=self.settings.sleep_time),
                RotateStartLayerPrint(self.settings.rotate_amount),
                AllWelderControl(), MoveUpZ(self.settings.weld_gap),
                AddMicerSettings(settings=self.settings),
            ],
            command_processor=[
                # OR HERE
                YourNewCuraCommandProcessor(),
                ExtruderRemover()
            ])
        new_gcode = gcode_pipeline.process(data)
```
