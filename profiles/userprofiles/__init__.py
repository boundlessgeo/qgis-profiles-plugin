# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.

import os
import glob
from qgis.core import *

from profiles.profile import Profile

profiles = {}

profileFiles = glob.glob(os.path.join(os.path.dirname(__file__), '*.json'))
for f in profileFiles:
    profile = Profile.fromFile(f)
    profiles[profile.name] = profile

folder = os.path.join(QgsApplication.qgisSettingsDirPath(), 'profiles')
filepath = os.path.join(folder, 'default.profile')
if os.path.exists(filepath):
	defaultProfile = Profile.fromFile(filepath)
	profiles[defaultProfile.name] = defaultProfile
