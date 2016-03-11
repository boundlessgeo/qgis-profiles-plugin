# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
import json
from qgis.utils import *
from PyQt4.QtGui import QToolBar, QDockWidget, QMessageBox
from PyQt4.QtCore import QSettings
import httplib2
from PyQt4.Qt import QDomDocument
from pyplugin_installer.qgsplugininstallerinstallingdialog import QgsPluginInstallerInstallingDialog
from qgis.gui import *

PLUGINS, MENUS, BUTTONS, PANELS = range(4)

def saveCurrentStatus(filepath, name, toAdd = None):
    toAdd = toAdd or range(4)
    status = {"name": name}
    if MENUS in toAdd:
        addMenus(status)
    if BUTTONS in toAdd:
        addButtons(status)
    if PANELS in toAdd:
        addPanels(status)
    if PLUGINS in toAdd:
        addPlugins(status)

    with open(filepath, "w") as f:
        json.dump(status, f)

def getMenus(path, action):
    menus = {}
    submenu = action.menu()
    if submenu is None:
        if not action.isSeparator():
            menus[path + "/" + action.objectName()] = action
    else:
        path = submenu.objectName() if path is None else path + "/" + submenu.objectName()
        actions = submenu.actions()
        for subaction in actions:
            menus.update(getMenus(path, subaction))
    return menus

def addMenus(status):
    menus = {}
    actions = iface.mainWindow().menuBar().actions()
    for action in actions:
        menus.update(getMenus(None, action))
    status["menus"] = {k:v.text() for k,v in menus.iteritems()}


def addPanels(status):
    status["panels"] =  [el.objectName() for el in iface.mainWindow().children()
                if isinstance(el, QDockWidget) and el.isVisible()]

def addPlugins(status):
    status["plugins"] = active_plugins

def addButtons(status):
    buttons = {}
    toolbars = [el for el in iface.mainWindow().children()
                if isinstance(el, QToolBar) and el.isVisible()]
    for bar in toolbars:
        barbuttons = [action.objectName() for action in bar.actions() if action.isVisible()]
        if barbuttons:
            buttons[bar.objectName()] = barbuttons

    status["buttons"] = buttons


def applyButtons(profile):
    if profile.buttons is None:
        return
    currentToolbars = [el for el in iface.mainWindow().children()
                if isinstance(el, QToolBar)]
    toolbars = profile.buttons
    for toolbar in currentToolbars:
        if toolbar.objectName() in toolbars:
            toolbar.setVisible(True)
            actions = toolbar.actions()
            for action in actions:
                action.setVisible(action.objectName() in toolbars[toolbar.objectName()])
        else:
            toolbar.setVisible(False)

def isMenuWhiteListed(path):
    return "mProfilesPlugin" in path

def applyMenus(profile):
    if profile.menus is None:
        return
    menus = {}
    actions = iface.mainWindow().menuBar().actions()
    for action in actions:
        menus.update(getMenus(None, action))

    for path, action in menus.iteritems():
        if path in profile.menus or isMenuWhiteListed(path):
            action.setVisible(True)
            action.setText(profile.menus.get(path, action.text()))
        else:
            action.setVisible(False)

    cleanEmptyMenus()

def cleanEmptyMenus():
    actions = iface.mainWindow().menuBar().actions()
    for action in actions:
        action.setVisible(cleanEmptySubmenus(action))

def cleanEmptySubmenus(action):
    menu = action.menu()
    actions = menu.actions()
    for act in actions:
        submenu = act.menu()
        if submenu is not None:
            act.setVisible(cleanEmptySubmenus(act))

    for act in actions:
        if not act.isSeparator() and act.isVisible():
            return True

    return False

def addActionAt(action, menuPath):
    pathLevels = menuPath.split("/")
    actions = iface.mainWindow().menuBar().actions()
    for name in pathLevels:
        menu = None
        for act in actions:
            _menu = act.menu()
            if _menu is not None and _menu.objectName() == name:
                menu = _menu
                break
        if menu is None:
            return
        actions = menu.actions()

    menu.addAction(action)

def applyPanels(profile):
    if profile.panels is None:
        return
    currentPanels = [el for el in iface.mainWindow().children()
                if isinstance(el, QDockWidget)]
    panels = profile.panels
    for panel in currentPanels:
        panel.setVisible(panel.objectName() in panels)


def applyPlugins(profile):
    if profile.plugins is None:
        return True
    toInstall = [p  for p in profile.plugins if p not in available_plugins]
    if toInstall:
        ok = QMessageBox.question(iface.mainWindow(), "Profile installation",
            "This profile requires plugins that are not currently\n"
            "available in your QGIS installation. The will have to\n"
            "be downloaded and installed.\n\n Do you want to proceed?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if ok != QMessageBox.Yes:
            return False
        for p in toInstall:
            installPlugin(p)

    updateAvailablePlugins()

    settings = QSettings()

    tounload = [p for p in active_plugins if p not in profile.plugins]
    for p in tounload:
        print p
        #this is a dirty trick. For some reason, calling unloadPlugin causes
        #all elements from qgis.utils to be None, so we have to reimport them
        #to avoid raising a exception
        from qgis.utils import unloadPlugin as unload
        unload(p)
        settings.setValue('/PythonPlugins/' + p, False)

    from qgis.utils import *
    updateAvailablePlugins()

    for p in profile.plugins:
        if p not in active_plugins:
            loadPlugin(p)
            startPlugin(p)
            settings.setValue('/PythonPlugins/' + p, True)
    updateAvailablePlugins()
    updatePluginManager()
    print active_plugins

    return True

def updatePluginManager():
    from pyplugin_installer.installer import QgsPluginInstaller
    from pyplugin_installer.installer_data import plugins
    installer = QgsPluginInstaller()
    plugins.getAllInstalled(testLoad=True)
    plugins.rebuild()
    installer.exportPluginsToManager()


pluginNodes = None
def installPlugin(pluginName):
    global pluginNodes
    if pluginNodes is None:
        resp, content = httplib2.Http().request("http://plugins.qgis.org/plugins/plugins.xml?qgis=2.12")
        if resp["status"] != "200":
            QMessageBox.critical(iface.mainWindow(), "Plugin installation",
                                    "Could not connect to plugin server.",
                                    QMessageBox.Ok, QMessageBox.Ok)
        reposXML = QDomDocument()
        reposXML.setContent(content.replace("& ", "&amp; "))
        pluginNodes = reposXML.elementsByTagName("pyqgis_plugin")
    for i in range(pluginNodes.size()):
        url = pluginNodes.item(i).firstChildElement("download_url").text().strip()
        if ("/%s/" % pluginName) in url:
            print pluginName
            name = pluginNodes.item(i).toElement().attribute("name")
            plugin = {"name":pluginName,
                    "id":pluginName,
                    "download_url":url,
                    "filename": pluginNodes.item(i).firstChildElement("file_name").text().strip()}
            dlg = QgsPluginInstallerInstallingDialog(iface.mainWindow(), plugin)
            dlg.exec_()
            if dlg.result():
                QMessageBox.critical(iface.mainWindow(), "Plugin installation",
                                ("The %s plugin could not be installed.\n"
                                "The following problems were found during installation:\n%s")
                                % (name, dlg.result()),
                                QMessageBox.Ok, QMessageBox.Ok)
            else:
                loadPlugin(pluginName)
                startPlugin(pluginName)
                updateAvailablePlugins()



def applyProfile(profile):
    if applyPlugins(profile):
        applyMenus(profile)
        applyButtons(profile)
        applyPanels(profile)
        iface.messageBar().pushMessage("Profiles", "Profile has been correctly applied",
                                       level=QgsMessageBar.INFO, duration=3)

