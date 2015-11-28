#!/usr/bin/env python
# -*- coding: utf-8 -*-

from example_sync import exampleSync
from reading_sync import readingSync

from aqt.qt import *
from anki.hooks import addHook


a = readingSync()
b = exampleSync()
addHook('browser.setupMenus', a.setupMenu)
addHook('browser.setupMenus', b.setupMenu)
addHook('editFocusLost', a.onFocusLost)
addHook('editFocusLost', b.onFocusLost)