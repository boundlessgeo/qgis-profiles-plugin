
# -*- coding: utf-8 -*-

import os
from PyQt4 import QtGui, QtCore
from userprofiles import profiles

class ProfilesPlugin:

	def __init__(self, iface):
		self.iface = iface
		QtCore.QSettings().setValue( '/UI/Customization/enabled', False)


	def unload(self):
		self.iface.removePluginMenu(u"Profiles", self.action)

	def initGui(self):
		icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), 'profiles.gif'))
		for k,v in profiles.iteritems():
			action = QtGui.QAction(icon, k, self.iface.mainWindow())
			action.triggered.connect(lambda _, menuName=k: self.applyProfile(menuName))
			self.iface.addPluginToMenu(u"Profiles", action)


		name = QtCore.QSettings().getValue( 'profilesplugin/LastProfile')
		if name in profiles:
			self.applyProfile(name)

	def applyProfile(self, name):
		QtCore.QSettings().setValue( 'profilesplugin/LastProfile', name)
		profile = profiles[name]
		profile.apply()



