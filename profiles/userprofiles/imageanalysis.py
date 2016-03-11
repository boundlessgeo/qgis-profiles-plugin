# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
from processing.gui.utils import *
from processing.core.Processing import Processing
from profilesplugin.utils import addActionAt
from qgis.utils import *
from catalogpl_plugin import CatalogPLPlugin
from PyQt4.Qt import QAction

def addProviderAsMenus(providerName, menuName):
    provider = Processing.getProviderFromName(providerName)
    for alg in provider.algs:
        addAlgorithmEntry(alg.commandLineName(), menuName, alg.group)

def apply():
    addProviderAsMenus("otb", "Image analysis")
    plugin = plugins["catalogpl_plugin"]
    action = QAction(plugin.icon, "Planet Labs layer", iface.mainWindow())
    action.triggered.connect(plugin.run)
    addActionAt(action, "mLayerMenu/mAddLayerMenu")
