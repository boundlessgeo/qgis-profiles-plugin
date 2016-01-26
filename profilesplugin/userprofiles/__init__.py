import glob
import os
from profilesplugin.profile import Profile
import importlib

profiles = {}
profileFiles = glob.glob(os.path.join(os.path.dirname(__file__), "*.json"))
for f in profileFiles:
    profile = Profile.fromFile(f)
    try:
        module = importlib.import_module('profilesplugin.userprofiles' + os.path.os.path.basename(f).splitext()[0])
    except ImportError:
        continue
    if hasattr(module, 'apply'):
        func = getattr(module, 'apply')
        profile._apply = func
    profiles[profile.name] = profile