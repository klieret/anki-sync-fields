#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict

# import the main window object (mw) from ankiqt
from aqt import mw
from aqt.qt import QAction, SIGNAL

from .util import get_kanjis
from .log import logger


# probably not worth building a completely fleshed out db class
# with getters and setters, but it should be easy to do that later
class Db(defaultdict):
    """ The Sync object will have an instance of this class as database.
    It will first loop over the source notes and updating the database with the
    information that we later add to the target notes.

    The database is grouped by the kanji to which the information belongs and
    several information items are collected in a list.
    One information item itself is a defaultdict of the form {'field_name': field_value}

    Please note that field1 should be unique for each information item!

    The database structure is the following:
        {
            kanji1: [
                        {field1: value1, field2: value2, ...},          < information item 1
                        {field1: other_value1, field2: value2, ...},    < information item 2
                        ...
                    ],
            kanji2: [
                        {field1: value1, field2: value2, ...},
                        ....
                    ],
            ...
        }

    Example:
        {
            u"試": [
                        {u"Expression": u"試験", u"Meaning": u"Exam", u"__DECK__": u"vocabulary"},
                        {u"Expression": u"試合", u"Meaning": u"Match", u"__DECK__": u"vocabulary"}
                   ],
            u"試験": [
                        {u"Expression": u"試験", u"Meaning": u"Exam", u"__DECK__": u"vocabulary"},
                    ],
        }

    Where the first dictionary is of type defaultdict(list) and the second one of
    type defaultdict(str). I.e. when accessing missing items, you will not get an IndexError
    but an empty list or string.
    """
    def __init__(self):
        super(Db, self).__init__(list)


class Sync(object):
    def __init__(self):
        # those attributes are to be overwritten in the subclasses.
        self.source_decks = []
        self.source_cards = []
        self.source_kanji_field = ''
        self.source_harvest_fields = ['']
        self.target_decks = []
        self.target_cards = []
        self.target_kanji_field = ''
        self.target_target_field = ''
        self.menu_item_name = ""

        self._db = Db()

    def setup_menu(self, browser):
        print(self.menu_item_name)
        a = QAction(self.menu_item_name, browser)
        browser.form.menuEdit.addAction(a)
        browser.connect(a, SIGNAL("triggered()"), self.update_all_target_cards)

    def add_all_notes_to_db(self):
        """ Build self.data """
        # loop through source_decks and build self.data
        for deck in self.source_decks:
            nids = mw.col.findCards("deck:%s" % deck)
            for nid in nids:
                card = mw.col.getCard(nid)
                note = card.note()
                self._add_note_to_db(note, deck)

    def _add_note_to_db(self, note, deck=""):
        # see db class docstring for explanation of the db structure
        # note: not updated
        for kanji in get_kanjis(note[self.source_kanji_field]):
            item = defaultdict(str)
            for sf in self.source_harvest_fields:
                item[sf] = note[sf]
            item["__DECK__"] = deck
            self._db[kanji].append(item)

    def update_all_target_cards(self):
        logger.debug("Sync all.")
        self.add_all_notes_to_db()
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
            self.update_target_card(note)

    def update_target_card(self, note):
        if self._db == {}:
            # self.data has not been initialized
            print("Initializing self.data")
            self.add_all_notes_to_db()
        kanjis = get_kanjis(note[self.source_kanji_field])
        logger.debug("Found kanjis %s" % ', '.join(kanjis))
        sub_dict = {}
        for kanji in kanjis:
            if kanji in self._db.keys():
                sub_dict[kanji] = self._db[kanji]
        note[self.target_target_field] = self.format_target_field_content(sub_dict)
        note.flush()  # don't forget!

    def format_target_field_content(self, sub_dict):
        # should be overriden in subclass
        raise NotImplementedError

    def on_focus_lost(self, flag, note, field):
        """ This method gets called as soon as somebody
        edits a field on a card, i.e. we use it to automatically update
        the target field accordingly. See http://ankisrs.net/docs/addons.html#hooks
        """
        model = note.model()['name']
        if model in self.source_cards:
            # Ignore it.
            # Some earlier versions tried to update our database
            # in this case. Note that in this case we would have to
            # take care of duplicates in the database and instead try to update
            # entries accordingly.
            # However, since it's on_focus_lost there's no guarantee that
            # the card is even added, so this only leads to coding effort
            # with questionable effects.
            return True
        elif model in self.target_cards:
            src_fields = [self.target_kanji_field]
            ok = False
            for c, name in enumerate(mw.col.models.fieldNames(note.model())):
                for f in src_fields:
                    if name == f:
                        if field == c:
                            ok = True
            if not ok:
                return flag
            self.update_target_card(note)
            return True
        else:
            return flag
