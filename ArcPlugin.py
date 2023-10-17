from UM.Extension import Extension
from UM.Scene.Selection import Selection
from UM.Math.Vector import Vector
from UM.Logger import Logger
from UM.i18n import i18nCatalog
import sys
import os
import pathlib

sys.path.append(os.path.abspath(os.path.join(pathlib.Path(__file__).parent,
                                             "./src")))
Logger.log("e", f"arcplugin_debug: after sys.path insert: Python Sys Path: {sys.path}")

i18n_catalog = i18nCatalog("ArcPlugin")
try:
    import arcgcode
    Logger.log("e", f"arcplugin_debug: imported arcgcode!")
except Exception as e:
    Logger.log("e", f"arcplugin_debug: error importing arcgcode: {str(e)}")


class ArcPlugin(Extension):
    def __init__(self):
        super().__init__()
        self.addMenuItem(i18n_catalog.i18n("Post-process G-Code"), self.convertToMetric)

    ##  Scales all selected objects by 25.4 (inch to mm)
    def convertToMetric(self):
        selected_nodes = Selection.getAllSelectedObjects()
        for node in selected_nodes:
            node.scale(Vector(25.4, 25.4, 25.4))
