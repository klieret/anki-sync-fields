#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Sets up logging to collect debugging information. """

import logging
import os.path
import sys

logger = logging.getLogger('sync_readings_logging')
logger.setLevel(logging.DEBUG)

sh_info = logging.StreamHandler(stream=sys.stdout)
sh_info.setLevel(logging.WARNING)

# will be caught by anki and displayed in a
# pop-up window
sh_error = logging.StreamHandler(stream=sys.stderr)
sh_error.setLevel(logging.ERROR)

addon_dir = os.path.dirname(__file__)
log_path = os.path.join(addon_dir, 'sync_readings.log')
fh = logging.FileHandler(log_path, mode="w")
fh.setLevel(logging.DEBUG)

logger.addHandler(fh)
logger.addHandler(sh_error)
logger.addHandler(sh_info)
