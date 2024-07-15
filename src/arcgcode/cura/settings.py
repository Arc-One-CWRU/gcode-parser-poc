from dataclasses import dataclass

@dataclass
class CuraMicerSettings:
    """Cura Micer Settings"""
    weld_gap: float
    sleep_time: float
    rotate_amount: float
    overwrite_movement_rate: bool
    movement_rate: float
    use_temperature_sensor: bool
    wait_for_temp: float
    pause_after_layer: bool
    return_home: bool
    change_initial_Z: bool
    change_G0toG1: bool

