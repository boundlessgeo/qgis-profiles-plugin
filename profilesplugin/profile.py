import json
from utils import applyProfile

class Profile():

    def __init__(self):
        self.name = ""
        self.panels = []
        self.buttons = {}
        self.menus = {}
        self._appply = None

    def apply(self):
        applyProfile(self)
        if self._apply is not None:
            self._apply()

    @staticmethod
    def fromFile(defFile):
        with open(defFile) as f:
            d = json.load(f)
        profile = Profile()
        profile.__dict__.update(d)
        return profile
