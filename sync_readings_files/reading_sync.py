#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sync import Sync
from .util import get_kanjis, clean

# import the main window object (mw) from ankiqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.qt import *

# todo: move to docstring
# adds the story etc. of the readings to the field 'readings_story'
# of the vocabulary notes.


class ReadingsSync(Sync):
    def __init__(self):
        """Mostly configuration stuff."""
        Sync.__init__(self)
        # todo: don't we init our super method?

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
        self.sourceFields = ['onyomi_story', 'kunyomi_story', 'combined_story', 'kanji_examples']
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

    # -------------------------------------  -------------------------------------

    def join_source_fields(self, sub_dict):
        """ Takes a subset of self.data and transforms it to
        the string to be written in the field self.targetField."""
        out = unicode("")
        for key in sub_dict.keys():
            on, kun, comb, ex = [sub_dict[key][self.sourceFields[i]].strip() for i in range(4)]
            out += '<span style="color:red">'+key+'</span>: '
            if on:
                out += "O: " + on
            if kun:
                out += "K: " + kun
            if comb:
                out += "C: " + comb
            if ex:
                out += " Ex.: " + clean(ex, ['<br>', '\n'], '; ').strip()
            out += "<br>"
        # split last <br>s
        if out[:-8] == "<br><br>":
            return out[:-8]
        else:
            return out[:-4]