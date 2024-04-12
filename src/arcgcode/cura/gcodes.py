from enum import Enum


# Maybe subclass for stuff to be remove versus total
class GCodes(Enum):
    TOOL = "T0"
    SET_EXTRUDER_TEMP = "M104"
    SET_EXTRUDER_TEMP_AND_WAIT = "M109"
    SET_EXTRUDER_TO_RELAITVE = "M83"
    SET_EXTRUDER_TO_ABOSULTE = "M82"
    FAN_OFF = "M107"
    WELD_OFF = "M42 P1 S0 ;Disable Welder\n"
    WELD_ON = "M42 P1 S1 ;Enable Welder\n"
    SLEEP = "G4"
    WAIT = "M116"
    PAUSE = "M226"
    WELD_OFF_MESSAGE = "M291 P\"Weld Off"
    WELD_ON_MESSAGE = "M291 P\"Weld On"
    INTERPASS_MACRO = "M98 P\"/macros/WaitForInterpassTemp.g\""
    