# -*- coding: utf-8 -*-

"""
qidata_gui package
==================

This package contains all widgets necessary to display data and any metadata linked to it.
It also contains several graphical applications using those widgets.
"""

import os, glob

# ––––––––––––––––––
# Export all modules

__all__ = [os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__)+"/*.py")]

try: del f # Cleanup the iteration variable so that it's not exported
except: pass

# ––––––––––––––––––––––––––––
# Convenience version variable

VERSION = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "VERSION")).read().split()[0]

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
