# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.

import os
import glob
from qgis.core import *
from qgis.utils import iface

from profiles.profile import Profile
from profiles.utils import saveCurrentStatus
from PyQt4.QtCore import QSettings
from PyQt4.QtGui import QMessageBox
import time

profiles = {}

profileFiles = glob.glob(os.path.join(os.path.dirname(__file__), '*.json'))
for f in profileFiles:
    profile = Profile.fromFile(f)
    profiles[profile.name] = profile


customProfiles = []

def customProfileFiles():
    customProfileFilepath = os.path.join(QgsApplication.qgisSettingsDirPath(), 'profiles')

    if os.path.exists(customProfileFilepath):
        return glob.glob(os.path.join(customProfileFilepath, '*.json'))
    else:
        return []

def hasCustomProfiles():
    return bool(customProfileFiles())

profileFiles = customProfileFiles()
for f in profileFiles:
    profile = Profile.fromFile(f)
    customProfiles.append(profile)

def storeCurrentConfiguration():
    global userProfile
    folder = os.path.join(QgsApplication.qgisSettingsDirPath(), 'profiles')
    filepath = os.path.join(folder, 'profile%s.json' % str(time.time()))
    name = time.strftime("%b %d %Y %H:%M:%S", time.gmtime(time.time()))
    description = "This profile was created based on your QGIS configuration at %s" % name
    if not os.path.exists(filepath):
        if not os.path.exists(folder):
            os.mkdir(folder)
        saveCurrentStatus(filepath, name, description=description)
        customProfiles.append(Profile.fromFile(filepath))
