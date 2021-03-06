#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Sets up logging to collect debugging information. """

import logging
import os.path
import sys

dump_database_after_full_loop = False
# If this is set to true, the database will be written to the log file as a
# huge string after Sync.loop_source_notes is called (i.e. after a full loop
# over all source notes was performed)
# This may not perform that well.

logger = logging.getLogger('sync_fields_logging')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('SyncFields:%(levelname)s:%(message)s')

sh_info = logging.StreamHandler(stream=sys.stdout)
sh_info.setLevel(logging.WARNING)
sh_info.setFormatter(formatter)

# will be caught by anki and displayed in a pop-up window
sh_error = logging.StreamHandler(stream=sys.stderr)
sh_error.setLevel(logging.ERROR)
sh_error.setFormatter(formatter)

addon_dir = os.path.dirname(__file__)
log_path = os.path.join(addon_dir, 'sync_fields.log')

logger.addHandler(sh_error)
logger.addHandler(sh_info)

logger.info("Saving log to file %s" % os.path.abspath(log_path))
fh = logging.FileHandler(log_path, mode="w")
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(fh)


def dump_database(db):
    """ Puts the string representation of the database into a file
    in the log directory.
    :type db: Db
    """
    # fixme: performs really bad of couse
    db_dump_path = os.path.join(addon_dir, 'db_dump.log')
    logger.debug("Dumping database to file %s" % os.path.abspath(db_dump_path))
    with open(db_dump_path, 'w') as db_dump_file:
        db_dump_file.write(str(db))
