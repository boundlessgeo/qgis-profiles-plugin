# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.

import os

from PyQt4 import uic
from PyQt4.QtCore import QSettings, QFileInfo
from PyQt4.QtGui import (QDialog,
                         QFileDialog,
                         QMessageBox
                        )

from profiles.utils import saveCurrentStatus

pluginPath = os.path.split(os.path.dirname(__file__))[0]
WIDGET, BASE = uic.loadUiType(
    os.path.join(pluginPath, 'ui', 'saveprofiledialogbase.ui'))


class SaveProfileDialog(BASE, WIDGET):
    def __init__(self, parent=None):
        super(SaveProfileDialog, self).__init__(parent)
        self.setupUi(self)

        self.btnBrowse.clicked.connect(self.saveProfile)

    def saveProfile(self):
        settings = QSettings()
        lastDirectory = settings.value('profilesplugin/lastProfileDirectory', '.')

        fileName = QFileDialog.getSaveFileName(self, self.tr('Save profile'),
            lastDirectory, self.tr('Profiles (*.json *.JSON)'))

        if fileName == '':
            return

        if not fileName.lower().endswith('.json'):
            fileName += '.json'

        self.leFilePath.setText(fileName)

        settings.setValue('profilesplugin/lastProfileDirectory',
            QFileInfo(fileName).absoluteDir().absolutePath())

    def reject(self):
        QDialog.reject(self)

    def accept(self):
        if self.leName.text() == '':
            QMessageBox.warning(self, self.tr('Empty profile name'),
                                self.tr('Please enter profile name!'))
            return

        if self.leFilePath.text() == '':
            QMessageBox.warning(self, self.tr('No output path'),
                                self.tr('Please enter valid output path!'))
            return

        saveCurrentStatus(self.leFilePath.text(), self.leName.text())

        QDialog.accept(self)
