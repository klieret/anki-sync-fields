#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import the main window object (mw) from ankiqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.qt import QAction, SIGNAL

from .util import get_kanjis
from .log import logger


class Sync(object):
    def __init__(self):
        self.target_decks = []
        self.source_decks = []
        self.target_cards = []
        self.source_cards = []
        self.source_match = ''
        self.target_match = ''
        self.source_fields = ['']
        self.target_field = ''
        self.menu_item_name = ""
        self.data = {}

    def setup_menu(self, browser):
        a = QAction(self.menu_item_name, browser)
        browser.form.menuEdit.addAction(a)
        browser.connect(a, SIGNAL("triggered()"), self.sync_all)

    def build_data(self):
        """ Build self.data """
        # loop through sourceDeck and build self.data
        self.data = {}
        for deck in self.source_decks:
            nids = mw.col.findCards("deck:%s" % deck)
            for nid in nids:
                card = mw.col.getCard(nid)
                note = card.note()
                self.add_note_to_db(note, deck)

    def add_note_to_db(self, note, deck):
        pass

    def sync_all(self):
        logger.debug("Sync all.")
        self.build_data()
        # get all note ids that should be updated
        nids = []
        for deck in self.target_decks:
            nids_plus = mw.col.findCards("deck:%s" % deck)
            nids += nids_plus
            logger.debug("Considering %d cards from target deck %s." % (len(nids_plus), deck))
        # loop over them
        for nid in nids:
            card = mw.col.getCard(nid)
            note = card.note()
            self.sync_single_target(note)

    def sync_single_target(self, note):
        if self.data == {}:
            # self.data has not been initialized
            print("Initializing self.data")
            self.build_data()
        kanjis = get_kanjis(note[self.source_match])
        logger.debug("Found kanjis %s" % ', '.join(kanjis))
        sub_dict = {}
        for kanji in kanjis:
            if kanji in self.data.keys():
                sub_dict[kanji] = self.data[kanji]
        note[self.target_field] = self.target_field_content(sub_dict)
        note.flush()  # don't forget!

    def target_field_content(self, sub_dict):
        return ""

    def on_focus_lost(self, flag, note, field):
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
        if model in self.source_cards:
            # here we react only if one of the sourceFields
            # from which we extract Information is changed
            # this is enough to handle cases of a new kanji-reading
            # added.
            src_fields = self.source_fields
            ok = False
            for c, name in enumerate(mw.col.models.fieldNames(note.model())):
                for f in src_fields:
                    if name == f:
                        if field == c:
                            ok = True
            if not ok:
                return flag
            self.add_note_to_db(note, "")  # todo: check that same deck?
            return True
        elif model in self.target_cards:
            src_fields = [self.target_match]
            ok = False
            for c, name in enumerate(mw.col.models.fieldNames(note.model())):
                for f in src_fields:
                    if name == f:
                        if field == c:
                            ok = True
            if not ok:
                return flag
            self.sync_single_target(note)
            return True
        else:
            return flag