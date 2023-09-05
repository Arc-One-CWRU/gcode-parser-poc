# September Deliverables <!-- omit in toc -->

## Table of Contents <!-- omit in toc -->

- [1. Cleanup Repository](#1-cleanup-repository)
- [2. Refactoring \& Unit Testing](#2-refactoring--unit-testing)
- [3. New Shapes!](#3-new-shapes)
- [4. Linting \& CI](#4-linting--ci)
- [5. Integration with Temperature Sensor](#5-integration-with-temperature-sensor)

## 1. Cleanup Repository

- Nuke the UI and components.
- [**Refactor the `framework` and `micer_content.py` to work in-tandem for Cura GCode generation.**](#2-refactoring--unit-testing)
  - Move `GCodes(Enum)` into its own file.
  - Unit-test components
  - E2E test GCode examples.
    - Add example "correct" G-Codes to compare with
- Nuke any unused files
  - `app.py`, `framework_cli.py`, `main.py`
- Update `requirements.txt` with the correct dependencies.
- Nuke `examples` folder.

## 2. Refactoring & Unit Testing

Refactor `Micer(Script)` to only have the `getSettingDataString` and `execute` methods. Move the other methods into other functions/classes depending on their use-case.

Definitions:

- **Line/Command transform:** an operation that transforms 1 line of the GCode
- **Section transform:** an operation that takes a whole "section" (i.e. a `;LAYER` section) as input and returns something

These include, but are not limited to:

1. `gcode_in_line`: Should be a generic function to skip processing certain GCode commands.
   - This seems to only be used in `remove_extruder` so we can maybe reuse the [`command.G1ExtruderRemover`](../framework/processsor/command/extruder_remover.py)
2. `remove_extruder`: See 1.
3. `all_welder_control`: I'm not sure what this is supposed to do **(Need to follow up with Michael)**
   1. **ChatGPT Summary:** In summary, this code appears to be parsing a list of lines, looking for lines that contain the letter "E," and modifying them based on certain conditions related to the presence or absence of "E." It uses regular expressions to extract and remove the "E" value from the lines and includes specific values from an enum in the output list based on whether "E" is present or not.
4. `move_up_z`: Does something to the Z coordinates using the weld gap
   - Seems to be a line transform.
5. `splitter`: Trivial to refactor + test.
6. `add_sleep`:
   - Split into:
     - `;TIME_ELAPSED` line transform
     - Add sleep right after `;LAYER`
       - Could do this through a layer transform
     - Replace `;TIME` commands with the proper `end_time` (line transform)
7. `add_micer_settings`: can become a line transform
8. `rotate_start_layer_print`: Move this into its own section transform?
   - This definitely needs to be unit tested.

## 3. New Shapes!

Test GCodes with shapes:

(TBD)

- X
- Y
- Z

## 4. Linting & CI

See the `CI` branch.

## 5. Integration with Temperature Sensor

Replace sleep with GCode command for wait to temperature.
