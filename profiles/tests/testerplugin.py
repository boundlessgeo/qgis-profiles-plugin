# Tests for the QGIS Tester plugin. To know more see
# https://github.com/boundlessgeo/qgis-tester-plugin

import unittest
import sys
import os
from qgis.core import QgsApplication

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

    #write tests here and return them
    return [userProfileAutosaveTest]

class UnitTests(unittest.TestCase):

    def setUp(self):
        pass


def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(UnitTests, 'test'))
    return suite

def unitTests():
    _tests = []
    _tests.extend(suite())
    return _tests


