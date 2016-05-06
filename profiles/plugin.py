# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.

import os
from PyQt4 import QtGui, QtCore

from qgis.core import QgsApplication

from profiles.utils import saveCurrentStatus
from userprofiles import profiles
from profiles.profile import Profile

icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), 'profile.png'))


class ProfilesPlugin:

    def __init__(self, iface):
        self.iface = iface
        QtCore.QSettings().setValue('/UI/Customization/enabled', False)

        try:
            from profiles.tests import testerplugin
            from qgistester.tests import addTestModule
            addTestModule(testerplugin, 'Profiles plugin')
        except:
            pass

        def initProfile():
            return
            name = QtCore.QSettings().value('profilesplugin/LastProfile')
            if name in profiles:
                profile = profiles[name]
                if not profile.hasToInstallPlugins():
                    profile.apply()

        iface.initializationCompleted.connect(initProfile)

    def unload(self):
        if self.profilesMenu is not None:
            self.profilesMenu.deleteLater()
        else:
            for action in self.actions:
                self.iface.removePluginMenu(u'Profiles', action)

    def initGui(self):
        self.actions = []
        for k, v in profiles.iteritems():
            action = QtGui.QAction(icon, k, self.iface.mainWindow())
            action.triggered.connect(lambda _, menuName=k: self.applyProfile(menuName))
            action.setObjectName('mProfilesPlugin_' + k)
            self.actions.append(action)
        actions = self.iface.mainWindow().menuBar().actions()
        settingsMenu = None
        self.profilesMenu = None
        for action in actions:
            if action.menu().objectName() == 'mSettingsMenu':
                settingsMenu = action.menu()
                self.profilesMenu = QtGui.QMenu(settingsMenu)
                self.profilesMenu.setObjectName('mProfilesPlugin')
                self.profilesMenu.setTitle('Profiles')
                for action in self.actions:
                    self.profilesMenu.addAction(action)
                settingsMenu.addMenu(self.profilesMenu)
                break
        if self.profilesMenu is None:
            for action in self.actions:
                self.iface.addPluginToMenu(u'Profiles', action)

    def applyProfile(self, name):
        folder = os.path.join(QgsApplication.qgisSettingsDirPath(), 'profiles')
        filepath = os.path.join(folder, 'default.profile')
        if not os.path.exists(filepath):
            if not os.path.exists(folder):
                os.mkdir(folder)
            saveCurrentStatus(filepath, 'Default')
            defaultProfile = Profile.fromFile(filepath)
            profiles[defaultProfile.name] = defaultProfile

            action = QtGui.QAction(icon, 'Default', self.iface.mainWindow())
            action.triggered.connect(lambda: self.applyProfile(defaultProfile.name))
            action.setObjectName('mProfilesPlugin_Default')
            if self.profilesMenu is None:
                self.iface.addPluginToMenu(u'Profiles', action)
            else:
                self.profilesMenu.addAction(action)

        QtCore.QSettings().setValue('profilesplugin/LastProfile', name)
        profile = profiles[name]
        profile.apply()
