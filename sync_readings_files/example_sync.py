#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sync import Sync
# todo: *
from util import *

# import the main window object (mw) from ankiqt
from aqt import mw
# import the "show info" tool from utils.py
# todo: *
from aqt.qt import *

# Adds words which contain a certain kanji to the 'kanji_examples' field
# of the readings deck


class ExampleSync(Sync):
    def __init__(self):
        Sync.__init__(self)
        self.target_decks = ["KANJI::readings"]
        self.source_decks = ["VOCAB::vocabular_main",
                             "VOCAB::vocab_new",
                             "VOCAB::vocab_kanji1000",
                             "VOCAB::vocab_saikin"]
        self.deck_tag_dict = {"VOCAB::vocabular_main": u"本",
                              "VOCAB::vocab_new": u"新",
                              "VOCAB::vocab_saikin": u"最",
                              "VOCAB::vocab_kanji1000": u"漢",
                              "": u"無"}
        self.garget_cards = ['readings']
        self.source_cards = ['myJapanese_example_sentences', 'myJapanese_reverse']
        self.source_match = 'Expression'
        self.target_match = 'Expression'
        self.source_fields = ['Reading', 'Meaning']
        self.target_field = 'kanji_examples'
        self.maxExamples = 5
        self.menu_item_name = "Sync Examples"

    def join_source_fields(self, sub_dict):
        """ Takes a subset of self.data and transforms it to
        the string to be written in the field self.targetField."""
        out = unicode("")
        for key in sub_dict.keys():
            for i in range(min(self.maxExamples, len(sub_dict[key][self.source_fields[0]]))):
                out += highlight_match(sub_dict[key][self.source_fields[0]][i].strip(), key)
                meaning = sub_dict[key][self.source_fields[1]][i].strip()
                # clean = case insensitive replace of list members with some string
                meaning = clean(meaning, ['\n', '<br>', '</div>', '</p>', ','], '; ')
                meaning = clean(meaning, ['<div>' ], '')
                meaning = clean(meaning, ['&nbsp;'], ' ')
                # only one meaning:
                meaning = meaning.split(';')[0]
                if meaning[:3] == '1. ':
                    meaning = meaning[3:]
                deck = unicode(self.deck_tag_dict[sub_dict[key]["DECK"][i]])
                out += " (%s) [%s]<br>" % (meaning.strip(), deck)
        # split last <br>
        return out[:-4]

    def datafy_single_note(self, note, deck):
        # self.data looks like this:
        # { kanji1 : { sourceField1Name : [ sourceFieldValue1, sourceFieldValue2, ...] },
        #            { sourceField2Name : [ sourceFieldValue1, sourceFieldValue2, ...] }
        #   kanji2 : ... }
        # where sourceFieldValue1, sourceFieldValue2 etc. belong to the same source note.

        # loop over all kanjis that are found in the sourceMatch field of the source note
        for kanji in get_kanjis(note[self.source_match]):

                # if there is no entry for that kanji in the database, create a blank one
                if kanji not in self.data:
                    self.data[kanji] = {}

                # now we look if there's an entry for the sourceFieldNames and if not
                # we create one with the value we just found
                for sourceField in self.source_fields:
                    if sourceField not in self.data[kanji]:
                        self.data[kanji][sourceField] = [note[sourceField]]

                # now at least one entry exists
                # maybe we have to update instead of adding new stuff
                if note[self.source_fields[0]] in self.data[kanji][self.source_fields[0]]:
                    # only update
                    index = self.data[kanji][self.source_fields[0]].index(note[self.source_fields[0]])
                    self.data[kanji][self.source_fields[1]][index] = note[self.source_fields[1]]
                else:
                    # append all
                    for sourceField in self.source_fields:
                        self.data[kanji][sourceField].append(note[sourceField])

                # doing the same thing with the deck value
                if "DECK" not in self.data[kanji]:
                    self.data[kanji]["DECK"] = [deck]
                else:
                    self.data[kanji]["DECK"].append(deck)