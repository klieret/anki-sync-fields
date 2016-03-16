#!/usr/bin/env python
# -*- coding: utf-8 -*-

from example_sync import ExampleSync
from reading_sync import ReadingsSync

from anki.hooks import addHook


a = ReadingsSync()
b = ExampleSync()
addHook('browser.setupMenus', a.setup_menu)
addHook('browser.setupMenus', b.setup_menu)
addHook('editFocusLost', a.on_focus_lost)
addHook('editFocusLost', b.on_focus_lost)