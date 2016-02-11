#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sync import Sync
from util import *

# import the main window object (mw) from ankiqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.qt import *


class ReadingsSync(Sync):
    def __init__(self):
        # todo: don't we init our super method?
        """Mostly configuration stuff."""

        # ------------------------------ Configuration ------------------------------

        # We sync from sourceDecks to targetDecks
        # Note that if you have sutargetDecks, e.g. a subdeck rtk2
        # to the deck KANJI, then the name of the deck is KANJI::rtk2
        self.sourceDecks = ["KANJI::readings"]
        self.targetDecks = ["VOCAB::vocabular_main",
                            "VOCAB::vocab_new",
                            "VOCAB::vocab_kanji1000",
                            "VOCAB::vocab_saikin"]
        # For the automated completion of fields, check
        # for the card type instead:
        self.sourceCards = ['readings']
        self.targetCards = ['myJapanese_example_sentences']
        # Compare the following fields from source and target
        self.sourceMatch = 'Expression'
        self.targetMatch = 'Expression'
        # Take data from field sourceField and write it to targetField
        self.sourceFields = ['story', 'kanji_examples']
        self.targetField = 'readings_story'
        self.menu_item_name = "Sync Reading stories"

        # ------------------------------------  -------------------------------------

        # For the first method, we will store all data here.
        self.data = {}

    def datafy_single_note(self, note, deck):
        # print("Datafy single")
        for kanji in get_kanjis(note[self.sourceMatch]):
            self.data[kanji] = {}
            self.data[kanji]["DECK"] = deck
            for sourceField in self.sourceFields:
                self.data[kanji][sourceField] = note[sourceField]

    def sync_single_target(self, note):
        if self.data == {}:
            # self.data has not been initialized
            print("Initializing self.data")
            self.build_data()
        kanjis = get_kanjis(note[self.sourceMatch])
        sub_dict = {}
        for kanji in kanjis:
            if kanji in self.data.keys():
                sub_dict[kanji] = self.data[kanji]
        note[self.targetField] = self.join_source_fields(sub_dict)
        note.flush()  # don't forget!

    # -------------------------------------  -------------------------------------

    def join_source_fields(self, sub_dict):
        """ Takes a subset of self.data and transforms it to
        the string to be written in the field self.targetField."""
        out = unicode("")
        for key in sub_dict.keys():
            out += '<span style="color:red">'+key+'</span>: '
            if sub_dict[key][self.sourceFields[0]].strip():
                out += sub_dict[key][self.sourceFields[0]].strip()
            if sub_dict[key][self.sourceFields[1]].strip():
                out += " Ex.: "+clean(sub_dict[key][self.sourceFields[1]], ['<br>', '\n'], '; ').strip()
            out += "<br>"
        # split last <br>s
        if out[:-8] == "<br><br>":
            return out[:-8]
        else:
            return out[:-4]