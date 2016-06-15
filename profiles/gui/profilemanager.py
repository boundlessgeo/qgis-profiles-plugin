from PyQt4 import QtGui, uic
import os
from collections import defaultdict
from profiles.userprofiles import *

WIDGET, BASE = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'ui', 'profilemanager.ui'))

class ProfileManager(BASE, WIDGET):

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.profilesTree.currentItemChanged.connect(self.currentItemChanged)

        self.webView.anchorClicked.connect(self.descriptionLinkClicked)
        self.webView.setOpenLinks(False)

        self.okButton.clicked.connect(self.close)
        self.saveButton.clicked.connect(self.saveCurrent)

        self.fillTree()

        self.setInfoText()


    def fillTree(self):
        self.profilesTree.clear()

        allProfiles = defaultdict(list)
        for v in profiles.values():
            allProfiles[v.group].append(v)

        profileIcon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), os.pardir,
                                               'icons', 'profile.png'))

        for group, groupProfiles in allProfiles.iteritems():
            groupItem = QtGui.QTreeWidgetItem()
            groupItem.setText(0, group)
            for profile in groupProfiles:
                profileItem = QtGui.QTreeWidgetItem()
                profileItem.profile = profile
                profileItem.isCustom = False
                profileItem.setText(0, profile.name)
                profileItem.setIcon(0, profileIcon)
                groupItem.addChild(profileItem)
            self.profilesTree.addTopLevelItem(groupItem)

        groupItem = QtGui.QTreeWidgetItem()
        groupItem.setText(0, "User profiles")
        for profile in customProfiles():
            profileItem = QtGui.QTreeWidgetItem()
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
        remove = '&nbsp;&nbsp;<a href="delete">Delete this profile</a>' if isCustom else ""
        if profile.plugins:
            plugins = "<p><b>This profile requires the following plugins</b>: %s</p>" % ", ".join(profile.plugins) 
        else:
            plugins = ""
        return ('''<h2>%s</h2>%s<br>%s<p><a href="set">Set this profile</a>%s</p>'''
                % (profile.name, profile.description, plugins, remove))

    def setInfoText(self):
        self.webView.setHtml("Click on a profile to display its description.")

    def currentItemChanged(self):
        item = self.profilesTree.currentItem()
        if item:
            if hasattr(item, "profile"):
                self.webView.setHtml(self.createDescription(item.profile, item.isCustom))
            else:
                self.setInfoText()
        else:
            self.setInfoText()

