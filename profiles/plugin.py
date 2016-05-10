# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.

import os

from PyQt4.QtGui import QAction, QActionGroup, QMenu
from PyQt4.QtCore import QSettings

from qgis.core import QgsApplication

from profiles.profile import Profile
from profiles.utils import saveCurrentStatus
from userprofiles import profiles
from profiles.profile import Profile


class ProfilesPlugin:

    def __init__(self, iface):
        self.iface = iface
        QSettings().setValue('/UI/Customization/enabled', False)

        try:
            from profiles.tests import testerplugin
            from qgistester.tests import addTestModule
            addTestModule(testerplugin, 'Profiles plugin')
        except:
            pass

        iface.initializationCompleted.connect(self.initProfile)

    def unload(self):
        if self.profilesMenu is not None:
            self.profilesMenu.deleteLater()
        else:
            for action in self.actions:
                self.iface.removePluginMenu(u'Profiles', action)

    def initGui(self):
        self.actions = []
        settings = QSettings()
        defaultProfile = settings.value('profilesplugin/LastProfile', 'Default', unicode)
        for k, v in profiles.iteritems():
            action = QAction(k, self.iface.mainWindow())
            action.setCheckable(True)
            if k == defaultProfile:
                action.setChecked(True)
            action.triggered.connect(lambda _, menuName=k: self.applyProfile(menuName))
            action.setObjectName('mProfilesPlugin_' + k)
            self.actions.append(action)

        actions = self.iface.mainWindow().menuBar().actions()
        settingsMenu = None
        self.profilesMenu = None
        self.profilesGroup = QActionGroup(self.iface.mainWindow())
        for action in actions:
            if action.menu().objectName() == 'mSettingsMenu':
                settingsMenu = action.menu()
                self.profilesMenu = QMenu(settingsMenu)
                self.profilesMenu.setObjectName('mProfilesPlugin')
                self.profilesMenu.setTitle('Profiles')
                for action in self.actions:
                    self.profilesGroup.addAction(action)
                    self.profilesMenu.addAction(action)
                settingsMenu.addMenu(self.profilesMenu)
                break

        if self.profilesMenu is None:
            for action in self.actions:
                self.iface.addPluginToMenu(u'Profiles', action)

    def applyProfile(self, name):
        settings = QSettings()
        settings.setValue('profilesplugin/LastProfile', name)
        profile = profiles[name]
        profile.apply()

    def initProfile(self):
        settings = QSettings()

        # Seems this is first run of the plugin, we need to save current
        # QGIS state as default profile
        if 'profilesplugin' not in settings.childGroups():
            folder = os.path.join(QgsApplication.qgisSettingsDirPath(), 'profiles')
            filepath = os.path.join(folder, 'default.json')
            if not os.path.exists(filepath):
                if not os.path.exists(folder):
                    os.mkdir(folder)
                saveCurrentStatus(filepath, 'Default')
                settings.setValue('profilesplugin/LastProfile', 'Default')
                defaultProfile = Profile.fromFile(filepath)
                profiles[defaultProfile.name] = defaultProfile

        # Restore last used profile
        profileName = settings.value('profilesplugin/LastProfile', 'Default', unicode)
        if profileName in profiles:
            profile = profiles[profileName]
            if not profile.hasToInstallPlugins():
                profile.apply()
