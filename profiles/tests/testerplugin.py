from builtins import str
# Tests for the QGIS Tester plugin. To know more see
# https://github.com/boundlessgeo/qgis-tester-plugin

import os
import sys
import time
import shutil
import unittest

from qgis.PyQt.QtCore import Qt, QDir, QSettings

from qgis.core import QgsApplication
from qgis.utils import (iface,
                        active_plugins,
                        available_plugins,
                        unloadPlugin,
                        loadPlugin,
                        startPlugin,
                        updateAvailablePlugins)

from profiles.profile import Profile, defaultProfile
from profiles.gui.profilemanager import ProfileManager
from profiles.utils import saveCurrentStatus, pluginsToIgnore, updatePluginManager


def applyProfile(profileFile):
    profile = Profile.fromFile(os.path.join(os.path.dirname(__file__), 'userprofiles', profileFile))
    profile.apply()
    return profile

def tempFolder():
    tempDir = os.path.join(str(QDir.tempPath()), "profilesplugin")
    if not QDir(tempDir).exists():
        QDir().mkpath(tempDir)
    return str(os.path.abspath(tempDir))

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

userProfileFolder = os.path.join(QgsApplication.qgisSettingsDirPath(), 'profiles')
newUserProfileFolder = os.path.join(QgsApplication.qgisSettingsDirPath(), 'profiles_')

def _deleteUserProfiles():
    if os.path.exists(userProfileFolder):
        shutil.move(userProfileFolder, newUserProfileFolder)

def _recoverUserProfiles():
    shutil.rmtree(userProfileFolder)
    if os.path.exists(newUserProfileFolder):
        shutil.move(newUserProfileFolder, userProfileFolder)

def _checkFileCreated():
    assert os.path.exists(userProfileFolder)

profileManager = None
def _openProfileManager():
    global profileManager
    if profileManager is None:
        profileManager = ProfileManager(iface.mainWindow())
        #profileManager.setWindowFlags(Qt.WindowStaysOnTopHint)
    profileManager.close()
    profileManager.show()

def _closeProfileManager():
    global profileManager
    if profileManager:
        profileManager.close()
        profileManager = None

def _runFunctions(funcs):
    for f in funcs:
        f()

def functionalTests():
    try:
        from qgistester.test import Test
    except:
        return []

    userProfileAutosaveTest = Test("""Check that user profile is saved on first execution""")
    userProfileAutosaveTest.addStep("Rename user profile folder", _deleteUserProfiles)
    userProfileAutosaveTest.addStep("Select any profile in the profiles menu")
    userProfileAutosaveTest.addStep("Check file was created", _checkFileCreated)
    userProfileAutosaveTest.setCleanup(_recoverUserProfiles)

    userProfileAutosaveFromManagerTest = Test("""Check that user profile is saved on first execution from Profiles Manager""")
    userProfileAutosaveFromManagerTest.addStep("Rename user profile folder", _deleteUserProfiles)
    userProfileAutosaveFromManagerTest.addStep("Select any profile and set it. "
                                               "Check that a new entry appears under the 'user profiles' group",
                                               prestep = _openProfileManager, isVerifyStep = True)
    userProfileAutosaveFromManagerTest.addStep("Check file was created", _checkFileCreated)
    userProfileAutosaveFromManagerTest.setCleanup(lambda: _runFunctions([_closeProfileManager, _recoverUserProfiles]))

    noMenusTest = Test("""Check that a profile with no buttons is correctly applied""")
    noMenusTest.addStep("Save previous state", _savePreviousState)
    noMenusTest.addStep("Apply profile", lambda: applyProfile("nobuttons.json"))
    noMenusTest.addStep("Verify no toolbar is visible")
    noMenusTest.setCleanup(_recoverPreviousState)

    noMenusFromManagerTest = Test("""Check that a profile is correctly applied from the Plugin Manager""")
    noMenusFromManagerTest.addStep("Save previous state", _savePreviousState)
    noMenusFromManagerTest.addStep("Open profile manager", lambda: _openProfileManager)
    noMenusFromManagerTest.addStep("Set the 'no buttons' profile. Verify it has been applied and no toolbar is visible", isVerifyStep=True)
    noMenusFromManagerTest.setCleanup(_recoverPreviousState)

    cannotInstallPlugin = Test("""Check that when a plugin cannot be installed, a warning is shown""")
    cannotInstallPlugin.addStep("Save previous state", _savePreviousState)
    cannotInstallPlugin.addStep("Apply profile", lambda: applyProfile("wrongplugin.json"))
    cannotInstallPlugin.addStep("Verify warning is displayed: 'profile applied with errors'")
    cannotInstallPlugin.setCleanup(_recoverPreviousState)

    correctlySetPanelsTest = Test("""Check that panels are correctly set by profile""")
    correctlySetPanelsTest.addStep("Save previous state", _savePreviousState)
    correctlySetPanelsTest.addStep("Apply profile", lambda: applyProfile("onlyonepanel.json"))
    correctlySetPanelsTest.addStep("Verify log panel is the only visible panel")
    correctlySetPanelsTest.setCleanup(_recoverPreviousState)

    correctlySetPythonConsoleTest = Test("""Check that Python console is correctly handled""")
    correctlySetPythonConsoleTest.addStep("Save previous state", _savePreviousState)
    correctlySetPythonConsoleTest.addStep("Apply profile", lambda: applyProfile("pythonconsole.json"))
    correctlySetPythonConsoleTest.addStep("Verify Python console is visible")
    correctlySetPythonConsoleTest.setCleanup(_recoverPreviousState)

    renameMenuTest = Test("""Check that menu rename is correctly performed""")
    renameMenuTest.addStep("Save previous state", _savePreviousState)
    renameMenuTest.addStep("Apply profile", lambda: applyProfile("renamemenu.json"))
    renameMenuTest.addStep("Verify Processing Toolbox menu entry has been renamed")
    renameMenuTest.setCleanup(_recoverPreviousState)

    customButtonsTest = Test("""Check that custom toolbars are correctly created""")
    customButtonsTest.addStep("Save previous state", _savePreviousState)
    customButtonsTest.addStep("Apply profile", lambda: applyProfile("onlynavigationtoolbar.json"))
    customButtonsTest.addStep("Verify map navigation toolbar is the only one visible, and is splitted into two toolbars",
                              isVerifyStep = True)
    customButtonsTest.addStep("Recover previous state", _recoverPreviousState)
    customButtonsTest.addStep("Verify navigation toolbar is not split anymore")

    def _enableProcessing():
        loadPlugin("processing")
        startPlugin("processing")
        QSettings().setValue('/PythonPlugins/processing', True)
        updateAvailablePlugins()
        updatePluginManager()
        assert "processing" in active_plugins

    processingIgnoredTest = Test("""Check Processing is ignored""")
    processingIgnoredTest.addStep("Enable Processing", _enableProcessing)
    processingIgnoredTest.addStep("Save previous state", _savePreviousState)
    processingIgnoredTest.addStep("Apply profile", lambda: applyProfile("noplugins.json"))
    processingIgnoredTest.addStep("Verify Processing menu is available")
    processingIgnoredTest.setCleanup(_recoverPreviousState)

    profilesPluginIgnoredTest = Test("""Check Profiles entries are ignored when setting up menus""")
    profilesPluginIgnoredTest.addStep("Save previous state", _savePreviousState)
    profilesPluginIgnoredTest.addStep("Apply profile", lambda: applyProfile("nomenus.json"))
    profilesPluginIgnoredTest.addStep("Verify Settings/Profiles menus are available")
    profilesPluginIgnoredTest.setCleanup(_recoverPreviousState)

    def _removeTestPlugin():
        unloadPlugin("what3words")
        updateAvailablePlugins()
        updatePluginManager()
        assert "what3words" not in available_plugins

    def _checkTestPlugin():
        assert "what3words" in active_plugins

    correctlyDownloadPluginTest = Test("""Check plugin is correctly downloaded and installed""")
    correctlyDownloadPluginTest.addStep("Save previous state", _savePreviousState)
    correctlyDownloadPluginTest.addStep("Manually remove what3words if installed")#TODO:automate this
    correctlyDownloadPluginTest.addStep("Apply profile", lambda: applyProfile("onlyoneplugin.json"))
    correctlyDownloadPluginTest.addStep("Verify plugin is installed", _checkTestPlugin)
    correctlyDownloadPluginTest.addStep("Verify Plugins/what3words plugin menu is available")
    correctlyDownloadPluginTest.setCleanup(_recoverPreviousState)

    folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "userprofiles")
    profilesCount = len([name for name in os.listdir(folder) if name.endswith(".json")])
    setMenuEntriesTest = Test("""Check that menu entries are correctly created""")
    setMenuEntriesTest.addStep("Verify settings/profiles menu has %i available profiles" % profilesCount)

    noEmptyMenusTest = Test("""Check that no empty menus are shown""")
    noEmptyMenusTest.addStep("Save previous state", _savePreviousState)
    noEmptyMenusTest.addStep("Apply profile", lambda: applyProfile("noemptymenus.json"))
    noEmptyMenusTest.addStep("Verify that the 'Layers/New Layer' menu does not exist")
    noEmptyMenusTest.setCleanup(_recoverPreviousState)

    createCustomProfileTest = Test("""Check that the current state is correctly saved in manager""")
    createCustomProfileTest.addStep("Rename user profile folder", _deleteUserProfiles)
    createCustomProfileTest.addStep("Create a new profile with the current configuration and check that the profile appears in the profiles tree",
                                                prestep = _openProfileManager, isVerifyStep = True)
    createCustomProfileTest.addStep("Click on the profile. In the description panel, click on 'delete profile' and check that the profile is deleted",
                                                prestep = _openProfileManager, isVerifyStep = True)
    createCustomProfileTest.setCleanup(lambda: _runFunctions([_closeProfileManager, _recoverUserProfiles]))

    expandBoxesInToolBarTest = Test("""Check boxes are expanded in toolbars""")
    expandBoxesInToolBarTest.addStep("Save previous state", _savePreviousState)
    expandBoxesInToolBarTest.addStep("Apply profile", lambda: applyProfile("decision_maker.json"))
    expandBoxesInToolBarTest.addStep("Verify search box in toolbar has a normal size (not too small)")
    expandBoxesInToolBarTest.setCleanup(_recoverPreviousState)

    customLayersTest = Test("""Check that custom layers are kept on profiles changing""")
    customLayersTest.addStep("Save previous state", _savePreviousState)
    customLayersTest.addStep("Apply profile", lambda: applyProfile("data_manager.json"))
    customLayersTest.addStep("Add raster layer using QuickMapServices plugin", isVerifyStep=False)
    customLayersTest.addStep("Apply profile", lambda: applyProfile("decision_maker.json"))
    customLayersTest.addStep("Verify that raster layer still loaded in project")
    customLayersTest.setCleanup(_recoverPreviousState)


    return [userProfileAutosaveTest, userProfileAutosaveFromManagerTest,
            noMenusTest, noMenusFromManagerTest, cannotInstallPlugin,
            correctlySetPanelsTest, renameMenuTest, customButtonsTest,
            processingIgnoredTest, profilesPluginIgnoredTest,
            correctlyDownloadPluginTest, setMenuEntriesTest, noEmptyMenusTest,
            createCustomProfileTest, correctlySetPythonConsoleTest,
            expandBoxesInToolBarTest, customLayersTest
            ]

class UnitTests(unittest.TestCase):

    def setUp(self):
        pass

    #===========================================================================
    # def testRoundTrip(self):
    #     profile = applyProfile("data_manager.json")
    #     filename = tempFilename("json")
    #     saveCurrentStatus(filename, profile.name)
    #     profile2 = Profile.fromFile(filename)
    #     self.assertEqual(set(profile.panels), set(profile2.panels))
    #     #self.assertEqual(set(profile.menus), set(profile2.menus))
    #     self.assertEqual(set(profile.plugins), set(profile2.plugins))
    #     self.assertEqual(set(profile.buttons), set(profile2.buttons))
    #===========================================================================


    def testCorrectlyLoadPlugins(self):
        defaultProfile.apply()
        profile = applyProfile("data_manager.json")
        for plugin in profile.plugins:
            self.assertTrue(plugin in active_plugins or plugin in pluginsToIgnore, "Plugin %s is not in active_plugins %s nor in pluginsToIgnore %s" % (plugin, active_plugins, pluginsToIgnore))

    def testCustomizationIsDisabled(self):
        self.assertEquals(QSettings().value('/UI/Customization/enabled'), False)

def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(UnitTests, 'test'))
    return suite

def unitTests():
    _tests = []
    _tests.extend(suite())
    return _tests

def run_tests():
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(suite())
