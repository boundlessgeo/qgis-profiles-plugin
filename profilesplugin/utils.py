import json
from qgis.utils import iface
from PyQt4.QtGui import QToolBar, QDockWidget

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
    status["menus"] = {k:v.text() for k,v in menus}


def addPanels(status):
    status["panels"] =  [el.objectName() for el in iface.mainWindow().children()
                if isinstance(el, QDockWidget) and el.isVisible()]

def addPlugins(status):
    pass

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

def applyMenus(profile):
    menus = {}
    actions = iface.mainWindow().menuBar().actions()
    for action in actions:
        menus.update(getMenus(None, action))

    for path, action in menus.iteritems():
        if path in profile.menus:
            action.setVisible(True)
            action.setText(profile.menus[path])
        else:
            action.setVisible(False)


def applyPanels(profile):
    currentPanels = [el for el in iface.mainWindow().children()
                if isinstance(el, QDockWidget)]
    panels = profile.panels
    for panel in currentPanels:
        panel.setVisible(panel.objectName() in panels)

def applyPlugins(profile):
    pass


def applyProfile(profile):
    applyPlugins(profile)
    applyButtons(profile)
    applyMenus(profile)
    applyPanels(profile)

