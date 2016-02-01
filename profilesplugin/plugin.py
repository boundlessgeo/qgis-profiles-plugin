
# -*- coding: utf-8 -*-

import os
from PyQt4 import QtGui, QtCore
from userprofiles import profiles

class ProfilesPlugin:

	def __init__(self, iface):
		self.iface = iface
		QtCore.QSettings().setValue( '/UI/Customization/enabled', False)

		def initProfile():
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
				self.iface.removePluginMenu(u"Profiles", action)

	def initGui(self):
		icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), 'profiles.gif'))
		self.actions = []
		for k,v in profiles.iteritems():
			action = QtGui.QAction(icon, k, self.iface.mainWindow())
			action.triggered.connect(lambda _, menuName=k: self.applyProfile(menuName))
			action.setObjectName("mProfilesPlugin_" + k)
			self.actions.append(action)
		actions = self.iface.mainWindow().menuBar().actions()
		settingsMenu = None
		self.profilesMenu = None
		for action in actions:
			if action.menu().objectName() == "mSettingsMenu":
				settingsMenu = action.menu()
				self.profilesMenu = QtGui.QMenu(settingsMenu)
				self.profilesMenu.setObjectName('mProfilesPlugin')
				self.profilesMenu.setTitle("Profiles")
				for action in self.actions:
					self.profilesMenu.addAction(action)
				settingsMenu.addMenu(self.profilesMenu)
				break
		if self.profilesMenu is None:
			for action in self.actions:
				self.iface.addPluginToMenu(u"Profiles", action)



	def applyProfile(self, name):
		QtCore.QSettings().setValue('profilesplugin/LastProfile', name)
		profile = profiles[name]
		profile.apply()



