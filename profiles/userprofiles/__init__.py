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



def customProfileFiles():
    customProfileFilepath = os.path.join(QgsApplication.qgisSettingsDirPath(), 'profiles')

    if os.path.exists(customProfileFilepath):
        return glob.glob(os.path.join(customProfileFilepath, '*.json'))
    else:
        return []

def hasCustomProfiles():
    return bool(customProfileFiles())

def customProfiles():
    _customProfiles = []
    profileFiles = customProfileFiles()
    for f in profileFiles:
        profile = Profile.fromFile(f)
        _customProfiles.append(profile)
    return _customProfiles

def storeCurrentConfiguration():
    global userProfile
    folder = os.path.join(QgsApplication.qgisSettingsDirPath(), 'profiles')
    filepath = os.path.join(folder, 'profile%s.json' % str(time.time()))
    name = time.strftime("%b %d %Y %H:%M:%S", time.gmtime(time.time()))
    description = "This profile was created based on your QGIS configuration at %s" % name
    if not os.path.exists(folder):
        os.mkdir(folder)
    saveCurrentStatus(filepath, name, description=description)

def applyProfile(profile):
    settings = QSettings()
    if (not hasCustomProfiles()):
        storeCurrentConfiguration()
        QMessageBox.information(None, "Profiles",
                            "This is the first time you use a profile.\n\n"
                            "Your current configuration has been saved, so you can go back to it anytime.\n\n"
                            "Use the 'Profiles/Profiles manager...' menu to do so.")
    if settings.contains('profilesplugin/LastProfile'):
        lastProfile =  settings.value('profilesplugin/LastProfile')
        settings.setValue("profilesplugin/Profiles/%s/geometry" % lastProfile,
                          iface.mainWindow().saveState())

    settings.setValue('profilesplugin/LastProfile', profile.name)

    profile.apply()
