# -*- coding: utf-8 -*-

def classFactory(iface):
    from plugin import ProfilesPlugin
    return ProfilesPlugin(iface)