import json
from utils import applyProfile
from qgis.utils import *

class Profile():

    def __init__(self):
        self.name = ""
        self.panels = []
        self.buttons = {}
        self.menus = {}
        self.plugins = []
        self._apply = None

    def apply(self):
        applyProfile(self)
        if self._apply is not None:
            self._apply()

    def hasToInstallPlugins(self):
        return any([(p not in plugins) for p in self.plugins])

    @staticmethod
    def fromFile(defFile):
        with open(defFile) as f:
            d = json.load(f)
        profile = Profile()
        profile.__dict__.update(d)
        return profile
