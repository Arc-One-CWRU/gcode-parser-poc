# Copyright (c) 2015 Jaime van Kessel
# The ArcPlugin is released under the terms of the AGPLv3 or higher.

from . import ArcPlugin
from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("ArcPlugin")


def getMetaData():
    return {}


def register(app):
    return {"extension": ArcPlugin.ArcPlugin()}
