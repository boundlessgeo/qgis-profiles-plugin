# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.

import os
import glob
from qgis.core import *

from profiles.profile import Profile
from profiles.utils import saveCurrentStatus
from PyQt4.QtCore import QSettings

profiles = {}

profileFiles = glob.glob(os.path.join(os.path.dirname(__file__), '*.json'))
for f in profileFiles:
    profile = Profile.fromFile(f)
    profiles[profile.name] = profile


userProfile = None
userProfileFilepath = os.path.join(QgsApplication.qgisSettingsDirPath(), 'profiles', 'userprofile.json')
if os.path.exists(userProfileFilepath):
    userProfile = Profile.fromFile(userProfileFilepath)


def storeCurrentConfiguration():
    folder = os.path.join(QgsApplication.qgisSettingsDirPath(), 'profiles')
    filepath = os.path.join(folder, 'userprofile.json')
    if not os.path.exists(filepath):
        if not os.path.exists(folder):
            os.mkdir(folder)
        saveCurrentStatus(filepath, 'Previous user configuration')
        #QSettings.setValue('profilesplugin/LastProfile', 'Default')
        userProfile = Profile.fromFile(filepath)


storeCurrentConfiguration()