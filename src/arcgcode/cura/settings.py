from dataclasses import dataclass

@dataclass
class CuraMicerSettings:
    """Cura Micer Settings"""
    weld_gap: float
    sleep_time: float
    rotate_amount: float
