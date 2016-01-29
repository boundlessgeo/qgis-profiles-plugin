import glob
import os
from profilesplugin.profile import Profile
import importlib

profiles = {}
profileFiles = glob.glob(os.path.join(os.path.dirname(__file__), "*.json"))
for f in profileFiles:
    profile = Profile.fromFile(f)
    try:
        module = importlib.import_module('profilesplugin.userprofiles' + os.path.splitext(os.path.basename(f))[0])
        if hasattr(module, 'apply'):
            func = getattr(module, 'apply')
            profile._apply = func
    except ImportError:
        pass

    profiles[profile.name] = profile