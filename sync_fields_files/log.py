#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Sets up logging to collect debugging information. """

import logging
import os.path
import sys

logger = logging.getLogger('sync_readings_logging')
logger.setLevel(logging.DEBUG)

# todo: set level higher once we have everything working
sh_info = logging.StreamHandler(stream=sys.stdout)
sh_info.setLevel(logging.WARNING)

# will be caught by anki and displayed in a pop-up window
sh_error = logging.StreamHandler(stream=sys.stderr)
sh_error.setLevel(logging.ERROR)

addon_dir = os.path.dirname(__file__)
log_path = os.path.join(addon_dir, 'sync_readings.log')

logger.addHandler(sh_error)
logger.addHandler(sh_info)

logger.debug("Saving log to file %s" % os.path.abspath(log_path))
fh = logging.FileHandler(log_path, mode="w")
fh.setLevel(logging.DEBUG)

logger.addHandler(fh)


def dump_database_for_debugging(db):
    """ Puts the string representation of the database into a file
    in the log directory.
    :type db: Db
    """
    return
    # fixme: performs really bad of couse
    # db_dump_path = os.path.join(addon_dir, 'db_dump.log')
    # logger.debug("Dumping database to file %s" % os.path.abspath(db_dump_path))
    # with open(db_dump_path, 'w') as db_dump_file:
    #     db_dump_file.write(str(db))
