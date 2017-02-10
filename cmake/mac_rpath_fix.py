#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
##
## Project: NextGIS Borsch build system
## Author: Dmitry Baryshnikov <dmitry.baryshnikov@nextgis.com>
## Author: Maxim Dubinin <maim.dubinin@nextgis.com>
## Copyright (c) 2016 NextGIS <info@nextgis.com>
## License: GPL v.2
##
################################################################################

import os
import shutil
import string
import subprocess
import sys
import multiprocessing
import glob

install_dir = 'inst'

old_rpath = sys.argv[1]

def run(args):
    print 'calling ' + string.join(args)
    try:
        subprocess.check_call(args)
        return True
    except subprocess.CalledProcessError, e:
        return False

if sys.platform != 'darwin':
    exit('Mac OS X only supported')
# Qt libraries put to the <NextGIS>/Library/Frameworks/Qt<Core,Gui, etc>.framework
# Qt plugins put to the <NextGIS>/Library/plugins/<4>/<codecs,sqldrivers, etc.>/*.dylib
repo_root = os.getcwd()
qt_path = os.path.join(repo_root, install_dir)
qt_install_lib_path = os.path.join(qt_path, 'PyQt4')
files = glob.glob(qt_install_lib_path + "/*.so")
for f in files:
    if not os.path.isdir(f):
        run(('install_name_tool', '-rpath', old_rpath, '@loader_path/../../../../Frameworks/', f))
