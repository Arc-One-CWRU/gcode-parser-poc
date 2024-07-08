from arcgcode.cura.settings import CuraMicerSettings


class ArcGcodeTestProcessor():
    def __init__(self, settings: CuraMicerSettings) -> None:
        self.settings = settings
    
    def execute(self) -> list[str]:
        pass