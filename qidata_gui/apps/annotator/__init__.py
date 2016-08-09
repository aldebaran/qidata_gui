# -*- coding: utf-8 -*-

import os, glob

# ––––––––––––––––––
# Export all modules

__all__ = [os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__)+"/*.py")]

try: del f # Cleanup the iteration variable so that it's not exported
except: pass

# ––––––––––––––––––––
# Hook for qiq plugins

QIQ_PLUGIN_PACKAGES = ["qiq"]

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
