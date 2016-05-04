# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
from processing.gui.menus import *
from processing.core.Processing import Processing
from profiles.utils import addActionAt
from qgis.utils import *
from catalogpl_plugin import CatalogPLPlugin
from PyQt4.Qt import QAction
from PyQt4.QtGui import QMessageBox

def addProviderAsMenus(providerName, menuName):
    provider = Processing.getProviderFromName(providerName)
    if provider.algs:
        for alg in provider.algs:
            addAlgorithmEntry(alg, menuName, alg.group)
    else:
        QMessageBox.warning(iface.mainWindow(), "Plugin installation",
                        "OTB provider is not configured in Processing.\n"
                        "Image analysis tools could not be configured.",
                        QMessageBox.Ok, QMessageBox.Ok) 	

def apply():
    addProviderAsMenus("saga", "Image analysis")
    plugin = plugins["catalogpl_plugin"]
    action = QAction(plugin.icon, "Planet Labs layer", iface.mainWindow())
    action.triggered.connect(plugin.run)
    addActionAt(action, "mLayerMenu/mAddLayerMenu")
