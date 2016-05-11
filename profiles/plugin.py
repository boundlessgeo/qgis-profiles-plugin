# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.

import os

from PyQt4.QtGui import QAction, QActionGroup, QMenu
from PyQt4.QtCore import QSettings

from qgis.core import QgsApplication

from qgis.utils import iface

from profiles.utils import saveCurrentStatus
from userprofiles import profiles, storeCurrentConfiguration, userProfile


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

        self.userProfileAction = None

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

        self.addUserProfile()

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

    def addUserProfile(self):
        if self.userProfileAction is None and userProfile is not None:
            separator = QAction('', iface.mainWindow())
            separator.setSeparator(True)
            self.actions.append(separator)
            self.userProfileAction = QAction(userProfile.name, iface.mainWindow())
            self.userProfileAction.triggered.connect(lambda: self.applyProfile(userProfile.name))
            self.actions.append(self.userProfileAction)


    def applyProfile(self, name):
        storeCurrentConfiguration()
        self.addUserProfile()
        settings = QSettings()
        settings.setValue('profilesplugin/LastProfile', name)
        profile = profiles.get(name, userProfile)
        profile.apply()

    def initProfile(self):

        settings = QSettings()

        # Restore last used profile
        profileName = settings.value('profilesplugin/LastProfile', '', unicode)
        if profileName in profiles:
            profile = profiles[profileName]
            if not profile.hasToInstallPlugins():
                profile.apply()
