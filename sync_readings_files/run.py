#!/usr/bin/env python
# -*- coding: utf-8 -*-

from anki.hooks import addHook
from example_sync import ExampleSync
from reading_sync import ReadingsSync

rs = ReadingsSync()
es = ExampleSync()

addHook('browser.setupMenus', rs.setup_menu)
addHook('browser.setupMenus', es.setup_menu)
addHook('editFocusLost', rs.on_focus_lost)
addHook('editFocusLost', es.on_focus_lost)
