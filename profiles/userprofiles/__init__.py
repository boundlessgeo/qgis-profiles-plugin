# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
import glob
import os
from profiles.profile import Profile
import importlib

profiles = {}
profileFiles = glob.glob(os.path.join(os.path.dirname(__file__), "*.json"))
for f in profileFiles:
    profile = Profile.fromFile(f)
    try:
        module = importlib.import_module('profiles.userprofiles.' + os.path.splitext(os.path.basename(f))[0])
        if hasattr(module, 'apply'):
            func = getattr(module, 'apply')
            profile._apply = func
    except ImportError:
        pass

    profiles[profile.name] = profile
