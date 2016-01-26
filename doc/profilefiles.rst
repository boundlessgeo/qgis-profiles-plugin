Profile files
--------------

A profile file contain all the elements needed to configure the QGIS interface according to a profile.

It's stored as a JSON file, with the following elements:

- panels: The names of panels to show, with their QT object names. These panels will be made visible. All other panels not listed here will be hidden

- menus: Dict of menus to display. Menus are referred with their full path (including names of all parent menus) used as keys of the dict. Values are the name of the menu entry, to allow renaming of the menu item.

- buttons: Buttons to be displayed in the toolbar. Grouped by toolbars and referenced using their QT object name.

- plugins: names of plugins to activate. If a plugin is not installed, installation should be proposed to the user when changing. If plugins to activate add menu entries to the menu bar, those menu entries should be added to the *menus* list, otherwise they wont be shown. This is configured like this to alow having a plugin enabled, but only have certain menus from it available, or even no menus at all (so the plugin is only available for other plugins or to be used programatically)


For each json file in the ``userprofiles`` folder, a Profile objec tis created and registered, and a menu entry corresponding to that profile will be added to the *Profiles* menu. If your profile requires more than what the json file allows to configure, you can add a python file with code to be run when applying the profile.

To do that, just add a python file with the same name as the json file that contains the profile description, and add a function called ``apply`` to it. That function will be run when the profile is applied.
