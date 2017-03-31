#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict

# import the main window object (mw) from ankiqt
from aqt import mw
from aqt.qt import QAction, SIGNAL

from .util import get_kanjis
from .log import logger, dump_database, dump_database_after_full_loop

# todo: docstrings


# probably not worth building a completely fleshed out db class
# with getters and setters, but it should be easy to do that later
class Db(defaultdict):
    """ The Sync object will have an instance of this class as database.
    It will first loop over the source notes and updating the database with the
    information that we later add to the target notes.

    The database behaves has the following structure:

       defaultdict({
          kanji1: [
                     defaultdict({field1: value1, field2: value2, ...}),
                     defaultdict({field1: other_value1, field2: value2, ...}),
                     ...
                  ],
          kanji2: [
                     defaultdict({field1: value1, field2: value2, ...}),
                     ....
                  ],
          ...
       })

    Example:

       defaultdict({
          u"試": [
                     defaultdict({u"Expression": u"試験", u"Meaning": u"Exam",
                                 u"__DECK__": u"vocabulary"}),
                     defaultdict({u"Expression": u"試合", u"Meaning": u"Match",
                                 u"__DECK__": u"vocabulary"})
                 ],
          u"試験": [
                     defaultdict({u"Expression": u"試験", u"Meaning": u"Exam",
                                 u"__DECK__": u"vocabulary"}),
                  ],
       })

    Where the first defaultdict is of type defaultdict(list) and the second
    one of type defaultdict(str). I.e. when accessing missing items,
    you will not get an IndexError but an empty list or string.

    Please note that field1 should be unique for each information item!
    """
    def __init__(self):
        super(Db, self).__init__(list)


class Sync(object):
    """ Objects of this type will do the syncing of information between notes.
    Does the following:
        * As soon as Anki's browser is opened, a menu is set up
          (setup_menu), which contains a button to sync information to the
          target notes.
        * When editing a target note (i.e. a note to which information should
          be added), the sync to this note is also performed (on_focus_lost)
        * When editing a source note, the information of this note is added
          to the db on_focus_lost
        * When the first sync operation is run, the whole source deck is
          scanned and the database is built initially."""

    def __init__(self):
        # those attributes are to be overwritten in the subclasses.
        self.source_decks = []
        self.source_card_names = []
        self.source_kanji_field = ''
        self.source_harvest_fields = ['']
        self.target_decks = []
        self.target_card_names = []
        self.target_kanji_field = ''
        self.target_target_field = ''
        self.menu_item_name = ""

        self._db = Db()

    def setup_menu(self, browser):
        """ Adds a menu item to Anki's browser. Will be called via hook.
        :param browser:
        :return:
        """
        # todo: add option to only perform this on the selected notes
        a = QAction(self.menu_item_name, browser)
        browser.form.menuEdit.addAction(a)
        browser.connect(a, SIGNAL("triggered()"), self.loop_target_notes)

    def loop_source_notes(self):
        """Loops over all notes of the source deck and calls _add_note_to_db
        to add the relevant information to the database.
        """
        # reset db
        self._db = Db()
        # loop through source_decks and build self.data
        logger.debug("Initializing database.")
        for deck in self.source_decks:
            # todo: better use findNotes?
            nids = mw.col.findCards("deck:%s" % deck)
            logger.debug("Found %d cards from source deck %s." %
                         (len(nids), deck))
            for nid in nids:
                card = mw.col.getCard(nid)
                note = card.note()
                self._add_note_to_db(note, deck)
        if dump_database_after_full_loop:
            dump_database(self._db)

    def _add_note_to_db(self, note, deck=""):
        """ Adds information from a single note to the database.
        :param note: Anki note object
        :param deck: (str) deck name
        """
        # see db class docstring for explanation of the db structure
        # note: not updated
        for kanji in get_kanjis(note[self.source_kanji_field]):
            item = defaultdict(str)
            for sf in self.source_harvest_fields:
                item[sf] = note[sf]
            item["__DECK__"] = deck
            self._db[kanji].append(item)

    def loop_target_notes(self):
        """ Loops over all notes in the target deck and calls
        write_to_target_note to write the relevant information to the
        target field.
        """
        logger.debug("Syncing to all target notes.")
        self.loop_source_notes()
        # get all note ids that should be updated
        nids = []
        for deck in self.target_decks:
            nids_plus = mw.col.findCards("deck:%s" % deck)
            nids += nids_plus
            logger.debug("Found %d cards from target deck %s." %
                         (len(nids_plus), deck))
        # loop over them
        for nid in nids:
            card = mw.col.getCard(nid)
            note = card.note()
            self.write_to_target_note(note)

    def write_to_target_note(self, note):
        """ Writes relevant information to target field
        :param note: Anki note object.
        """
        if not self._db:
            # self.data has not been initialized, so do it now
            self.loop_source_notes()
        kanjis = get_kanjis(note[self.source_kanji_field])
        sub_dict = {}
        for kanji in kanjis:
            if kanji in self._db.keys():
                sub_dict[kanji] = self._db[kanji]
        note[self.target_target_field] = \
            self.format_target_field_content(sub_dict)
        note.flush()

    def format_target_field_content(self, sub_dict):
        # should be overriden in subclass
        raise NotImplementedError

    def on_focus_lost(self, flag, note, edited_field_no):
        """ This method gets called after a field on a card was edited
        in Anki. We use that to automatically update the target field
        accordingly.
        :param flag
        :param edited_field_no: The field number that has just lost focus.
        :type edited_field_no: int
        :param note: Anki note that is currently edited.
        :type note: Anki note
        """
        # Note: Not easy to check for the deck, so we only check the type of
        #   the card. Thus everything here applies to all cards of type in
        #   self.target_card regardless of the deck.

        # 1. Check that the card belongs to the target cards
        card_name = note.model()['name']
        # print "focus lost"
        logger.debug("Focus lost: flag: {}, note: {}, field: {}, "
                     "card: {}".format(flag, note, edited_field_no, card_name))
        if card_name in self.source_card_names:
            # Ignore it.
            # Some earlier versions tried to update our database
            # in this case. Note that in this case we would have to
            # take care of duplicates in the database and instead try to update
            # entries accordingly.
            # However, since it's on_focus_lost there's no guarantee that
            # the card is even added, so this only leads to coding effort
            # with questionable effects.
            return flag
        elif card_name in self.target_card_names:
            # 2. Check that the field that has lost focus is the one we're
            #    interested in
            relevant_fields = [self.target_kanji_field]
            # because we both deal with field names and field numbers
            # (we get edited_field_no as parameter, we have loop, enumerate
            # and compare numbers
            for field_no, field in \
                    enumerate(mw.col.models.fieldNames(note.model())):
                for releant_field in relevant_fields:
                    if field == releant_field and edited_field_no == field_no:
                            logger.debug("Focus lost > Update!")
                            self.write_to_target_note(note)
                            return True
            # we're not interested in this field
            return flag
        else:
            return flag
