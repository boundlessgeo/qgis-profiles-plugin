# Tests for the QGIS Tester plugin. To know more see
# https://github.com/boundlessgeo/qgis-tester-plugin

import unittest
import os
from qgis.core import QgsApplication
from profiles.profile import Profile, defaultProfile
from PyQt4 import QtCore
import time
from profiles.utils import saveCurrentStatus, pluginsToIgnore
from qgis.utils import iface, active_plugins

def applyProfile(profileFile):
    profile = Profile.fromFile(os.path.join(os.path.dirname(__file__), 'userprofiles', profileFile))
    profile.apply()
    return profile

def tempFolder():
    tempDir = os.path.join(unicode(QtCore.QDir.tempPath()), "profilesplugin")
    if not QtCore.QDir(tempDir).exists():
        QtCore.QDir().mkpath(tempDir)
    return unicode(os.path.abspath(tempDir))

def tempFilename(ext):
    path = tempFolder()
    ext = "" if ext is None else ext
    filename = path + os.sep + str(time.time())  + "." + ext
    return filename

previousStateFilename = None
def _savePreviousState():
    global previousStateFilename
    previousStateFilename = tempFilename("json")
    saveCurrentStatus(previousStateFilename, "temp")

def _recoverPreviousState():
    global previousStateFilename
    if previousStateFilename:
        profile = Profile.fromFile(previousStateFilename)
        profile.apply()
        previousStateFilename = None

def functionalTests():
    try:
        from qgistester.test import Test
    except:
        return []

    userProfileFile = os.path.join(QgsApplication.qgisSettingsDirPath(), 'profiles', 'userprofile.json')
    newUserProfileFile = os.path.join(QgsApplication.qgisSettingsDirPath(), 'profiles', '_userprofile.json')

    def _deleteUserProfile():
        if os.path.exists(userProfileFile):
            os.rename(userProfileFile, newUserProfileFile)

    def _recoverUserProfile():
        os.remove(userProfileFile)
        if os.path.exists(newUserProfileFile):
            os.rename(newUserProfileFile, userProfileFile)

    def _checkFileCreated():
        assert os.path.exists(userProfileFile)

    userProfileAutosaveTest = Test("""Check that user profile is saved on first execution""")
    userProfileAutosaveTest.addStep("Rename user profile", _deleteUserProfile)
    userProfileAutosaveTest.addStep("Select any profile in the profiles menu")
    userProfileAutosaveTest.addStep("Check file was created", _checkFileCreated)
    userProfileAutosaveTest.setCleanup(_recoverUserProfile)

    noMenusTest = Test("""Check that a profile with no buttons is correctly applied""")
    noMenusTest.addStep("Save previous state", _savePreviousState)
    noMenusTest.addStep("Apply profile", lambda: applyProfile("nobuttons.json"))
    noMenusTest.addStep("Verify no toolbar is visible")
    noMenusTest.setCleanup(_recoverPreviousState)

    cannotInstallPlugin = Test("""Check that when a plugin cannot be installed, a warning is shown""")
    cannotInstallPlugin.addStep("Save previous state", _savePreviousState)
    cannotInstallPlugin.addStep("Apply profile", lambda: applyProfile("wrongplugin.json"))
    cannotInstallPlugin.addStep("Verify warning is displayed and correctly applied")
    cannotInstallPlugin.setCleanup(_recoverPreviousState)



    #write tests here and return them
    return [userProfileAutosaveTest, noMenusTest, cannotInstallPlugin]

class UnitTests(unittest.TestCase):

    def setUp(self):
        pass

    def testRoundTrip(self):
        profile = applyProfile("data_manager.json")
        filename = tempFilename("json")
        saveCurrentStatus(filename, profile.name)
        profile2 = Profile.fromFile(filename)
        self.assertEqual(profile, profile2)

    def testCorrectlyLoadPlugins(self):
        defaultProfile.apply()
        profile = applyProfile("data_manager.json")
        for plugin in profile.plugins:
            self.assertTrue(plugin in active_plugins or plugin in pluginsToIgnore)

def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(UnitTests, 'test'))
    return suite

def unitTests():
    _tests = []
    _tests.extend(suite())
    return _tests


