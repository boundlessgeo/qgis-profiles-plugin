# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.

def apply():
    try:
        from processing.core.Processing import Processing
        Processing.activateProvider("ntv2_transformations")
    except:
        pass
