# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
import json
from utils import applyProfile
from qgis.utils import *

class Profile():

    def __init__(self):
        self.name = ""
        self.panels = None
        self.buttons = None
        self.menus = None
        self.plugins = None
        self._apply = None

    def apply(self):
        applyProfile(self)
        if self._apply is not None:
            self._apply()

    def hasToInstallPlugins(self):
        if self.plugins is None:
            return False
        return any([(p not in plugins) for p in self.plugins])

    @staticmethod
    def fromFile(defFile):
        with open(defFile) as f:
            d = json.load(f)
        profile = Profile()
        profile.__dict__.update(d)
        return profile
