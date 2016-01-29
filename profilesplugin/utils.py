import json
from qgis.utils import *
from PyQt4.QtGui import QToolBar, QDockWidget, QMessageBox
import httplib2
from PyQt4.Qt import QDomDocument
from pyplugin_installer.qgsplugininstallerinstallingdialog import QgsPluginInstallerInstallingDialog
from qgis.gui import *

def saveCurrentStatus(filepath, name):
    status = {"name": name}
    addMenus(status)
    addButtons(status)
    addPanels(status)
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
    currentToolbars = [el for el in iface.mainWindow().children()
                if isinstance(el, QToolBar)]
    toolbars = profile.buttons
    for toolbar in currentToolbars:
        if toolbar.objectName() in toolbars:
            toolbar.setVisible(True)
            for action in toolbar.actions():
                action.setVisible(action.objectName() in toolbars[toolbar.objectName()])
        else:
            toolbar.setVisible(False)

def isMenuWhiteListed(path):
    return "mProfilesPlugin" in path

def applyMenus(profile):
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


def applyPanels(profile):
    currentPanels = [el for el in iface.mainWindow().children()
                if isinstance(el, QDockWidget)]
    panels = profile.panels
    for panel in currentPanels:
        panel.setVisible(panel.objectName() in panels)


def applyPlugins(profile):
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

    for p in active_plugins:
        if p not in profile.plugins:
            #this is a dirty trick. For some reason, calling unloadPlugin causes
            #all elements from qgis.utils to be None, so we have to reimport them
            #to avoid raising a exception
            from qgis.utils import unloadPlugin as unload
            unload(p)
            from qgis.utils import updateAvailablePlugins as update
            update()

    from qgis.utils import *
    for p in profile.plugins:
        if p not in active_plugins:
            loadPlugin(p)
            startPlugin(p)

    updateAvailablePlugins()

    return True

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
        applyButtons(profile)
        applyMenus(profile)
        applyPanels(profile)
        iface.messageBar().pushMessage("Profiles", "Profile has been correctly applied",
                                       level=QgsMessageBar.INFO, duration=3)

