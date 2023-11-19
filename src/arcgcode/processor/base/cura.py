# Cura Layer Types (Constants)
CURA_LAYER = ";LAYER:"
CURA_MESH_LAYER = ";MESH"
CURA_OUTER_WALL = ";TYPE:WALL-OUTER"
# This can match with many layers, such as:
# ;TYPE:SKIN, ;TYPE:WALL-INNER, ;TYPE:WALL-OUTER, ;TYPE:SUPPORT, ;TYPE:FILL
CURA_TYPE_LAYER = ";TYPE"

# MARLIN

# Looks like ;MAXZ:19.95
# ;Generated with XYZ should be right after.
END_OF_HEADER_SETTINGS_MARLIN = ";MAXZ:"
END_OF_HEADER_SETTINGS_GRIFFIN = ";END_OF_HEADER"

# Cura specific constants.
END_OF_TOP_METADATA = ";Generated with"
END_OF_STARTUP_SCRIPT = ";LAYER_COUNT:"
# This is only the end if the flavor is Marlin
END_OF_GCODE_MOVEMENTS = ";TIME_ELAPSED"
END_OF_GCODE = ";End of Gcode"


def is_end_of_gcode_movements(gcode_line: str, curr_idx: int,
                              all_gcode_lines: list[str]) -> bool:
    """Checks to see if the current line is the end of the GCode movements
    section.

    Args:
        gcode_line: the line of a G-Code
        curr_idx: the index of all_gcode_lines where the current gcode_line is
        at
        all_gcode_lines: a list of all gcode instructions
    """
    at_boundary = gcode_line.startswith(END_OF_GCODE_MOVEMENTS)
    if not at_boundary:
        return False

    next_line_is_end_script = True
    if len(all_gcode_lines) - 1 > curr_idx:
        next_line = all_gcode_lines[curr_idx+1]
        # When the Cura flavor is Griffin, there is a TIME_ELAPSED
        # after each layer, so need to make sure that this is the
        # final TIME_ELAPSED
        #
        # Kinda hacky tbh...
        # But, the alternative would be to literally iterate through the
        # rest of the lines in the movements section to check if there's
        # another TIME_ELAPSED.
        #
        # But, that is computationally expensive O(N*NUM_LAYERS) in the worst
        # case.
        if (next_line.startswith(";TYPE") or
           next_line.startswith(";LAYER") or
           next_line.startswith(";MESH")):
            next_line_is_end_script = False

    return at_boundary and next_line_is_end_script
