#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import the main window object (mw) from ankiqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.qt import *

class sync():
    def __init__(self):
        self.targetDecks = []
        self.sourceDecks = []
        self.targetCards = []
        self.sourceCards = []
        self.sourceMatch = ''
        self.targetMatch = ''
        self.sourceFields = ['']
        self.targetField = ''
        self.menu_item_name = ""

    def setupMenu(self, browser):
        a = QAction(self.menu_item_name,browser)
        browser.form.menuEdit.addAction(a)
        browser.connect(a, SIGNAL("triggered()"), self.syncAll)

    def buildData(self):
        """ Build self.data """
        # loop through sourceDeck and build self.data
        self.data = {}
        for deck in self.sourceDecks:
            nids = mw.col.findCards("deck:%s" % deck)
            for nid in nids:
                card = mw.col.getCard(nid)
                note = card.note()
                self.datafySingleNote(note, deck)

    def datafySingleNote(self,note,deck):
        pass

    def syncAll(self):
        self.buildData()
        # get all note ids that should be updated
        nids = []
        for deck in self.targetDecks:
            nids += mw.col.findCards("deck:%s" % deck)
        # loop over them
        for nid in nids:
            card = mw.col.getCard(nid)
            note = card.note()
            self.syncSingleTarget(note)

    def syncSingleTarget(self,note):
        pass


    def joinSourceFields(self,subDict):
        return ""


    def onFocusLost(self,flag,note,field):
        """ this method gets called as soon as somebody
        edits a field on a card, i.e. we use it to automatically update
        the target field accordingly. See http://ankisrs.net/docs/addons.html#hooks """
        # first we check if this is a card
        # we're interested in:
        # Case 1:   Somebody changes something in sourceModel
        #           then we update self.data (but don't sync automatically)
        # Case 2:   Somebody changes something in targetModel
        #           then we sync
        # whenever a card is irrelevant, we return $flag
        model = note.model()['name']
        if model in self.sourceCards:
            # here we react only if one of the sourceFields
            # from which we extract Information is changed
            # this is enough to handle cases of a new kanji-reading
            # added.
            srcFields = self.sourceFields
            ok = False
            for c, name in enumerate(mw.col.models.fieldNames(note.model())):
                for f in srcFields:
                    if name == f:
                        if field == c:
                            ok = True
            if not ok:
                return flag
            self.datafySingleNote(note, "") # todo: deck!
            return True
        elif model in self.targetCards:
            srcFields = [self.targetMatch]
            ok = False
            for c, name in enumerate(mw.col.models.fieldNames(note.model())):
                for f in srcFields:
                    if name == f:
                        if field == c:
                            ok = True
            if not ok:
                return flag
            self.syncSingleTarget(note)
            return True
        else:
            return flag