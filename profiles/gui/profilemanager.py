# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.

import os
from collections import defaultdict

from PyQt4 import uic
from PyQt4.QtGui import QIcon, QPushButton, QDialogButtonBox, QTreeWidgetItem

from profiles.userprofiles import *

WIDGET, BASE = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'ui', 'profilemanager.ui'))


class ProfileManager(BASE, WIDGET):

    def __init__(self, parent):
        super(ProfileManager, self).__init__(parent)
        self.setupUi(self)

        self.profilesTree.currentItemChanged.connect(self.currentItemChanged)

        self.webView.anchorClicked.connect(self.descriptionLinkClicked)
        self.webView.setOpenLinks(False)

        self.btnSave = QPushButton(self.tr('Save current configuration as profile'))
        self.btnSave.clicked.connect(self.saveCurrent)

        self.buttonBox.addButton(self.btnSave, QDialogButtonBox.ActionRole)

        self.fillTree()

        self.setInfoText()

    def fillTree(self):
        self.profilesTree.clear()

        allProfiles = defaultdict(list)
        for v in profiles.values():
            allProfiles[v.group].append(v)

        profileIcon = QIcon(os.path.join(os.path.dirname(__file__), os.pardir,
                                               'icons', 'profile.png'))

        for group, groupProfiles in allProfiles.iteritems():
            groupItem = QTreeWidgetItem()
            groupItem.setText(0, group)
            for profile in groupProfiles:
                profileItem = QTreeWidgetItem()
                profileItem.profile = profile
                profileItem.isCustom = False
                profileItem.setText(0, profile.name)
                profileItem.setIcon(0, profileIcon)
                groupItem.addChild(profileItem)
            self.profilesTree.addTopLevelItem(groupItem)

        groupItem = QTreeWidgetItem()
        groupItem.setText(0, self.tr("User profiles"))
        for profile in customProfiles():
            profileItem = QTreeWidgetItem()
            profileItem.profile = profile
            profileItem.isCustom = True
            profileItem.setText(0, profile.name)
            profileItem.setIcon(0, profileIcon)
            groupItem.addChild(profileItem)
        self.profilesTree.addTopLevelItem(groupItem)

        self.profilesTree.expandAll()

    def saveCurrent(self):
        storeCurrentConfiguration()
        self.fillTree()

    def descriptionLinkClicked(self, url):
        profile = self.profilesTree.currentItem().profile
        if url.toString() == "set":
            applyProfile(profile)
            self.fillTree()
        else:
            os.remove(profile._filename)
            self.fillTree()

    def createDescription(self, profile, isCustom):
        remove = self.tr('&nbsp;&nbsp;<a href="delete">Delete this profile</a>') if isCustom else ""
        if profile.plugins:
            plugins = self.tr("<p><b>This profile requires the following plugins</b>: %s</p>") % ", ".join(profile.plugins)
        else:
            plugins = ""
        return (self.tr('''<h2>%s</h2>%s<br>%s<p><a href="set">Set this profile</a>%s</p>''')
                % (profile.name, profile.description, plugins, remove))

    def setInfoText(self):
        self.webView.setHtml(self.tr("Click on a profile to display its description."))

    def currentItemChanged(self):
        item = self.profilesTree.currentItem()
        if item:
            if hasattr(item, "profile"):
                self.webView.setHtml(self.createDescription(item.profile, item.isCustom))
            else:
                self.setInfoText()
        else:
            self.setInfoText()
