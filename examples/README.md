# Examples

## What are the biggest differences between the original GCode and the edited GCode?

The only differences are in the instructions:

- Original:

  ```
  M105 ;get temperature report
  M109 S0 ;waits for hotend temperature to target temperature 0
  M82 ;absolute extrusion mode
  G28 ;Home

  G92 E0 ;sets current position as extruder position 0
  G92 E0
  ;LAYER_COUNT:2
  ;LAYER:0
  M107 ;turn fan off
  ;MESH:WeldingLineTest.STL
  G0 F600 X342.474 Y120 Z0.3
  ;TYPE:WALL-OUTER
  G1 F60 X312.526 Y120 E5.63198

  M42 P1 S0
  G4 S5
  G28
  M82 ;absolute extrusion mode
  ```

- New:

  ```
  G28;Home
  G1 Z60 F6000; Raise the welding tip

  G0 F600 X342.474 Y120; Move to the starting spot
  G0 F6000 Z0.3; Lower the tip

  M42 P1 S1; Turn on the welder

  G1 F60 X312.526 Y120; Movement G-code

  M42 P1 S0; Turn off the welder
  G0 F20000 Z60; Raises the welding tip, quickly (F sets speed)
  ```

**Steps:**

1. Remove all gcode instructiosn before `G28`.
2. Raise the welding tip `G1 Z60 F6000` right after homing, move to the starting point and lower the tip.
3. Turn on the welder
4. Delete `M107`
5. Delete `G92 E0`
6. Move gun!
7. Turn off the welder
8. Remove gcode after turning off welder and raise welding tip right after turning off the welder: `G0 F20000 Z60`
