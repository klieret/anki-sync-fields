#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sync import Sync
# todo: *
from util import *

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
        self.target_cards = ['readings']
        self.source_cards = ['myJapanese_example_sentences', 'myJapanese_reverse']
        self.source_match = 'Expression'
        self.target_match = 'Expression'
        # todo: split up to make better to configure?
        self.source_fields = ['Reading', 'Meaning']
        self.target_field = 'kanji_examples'
        self.max_examples = 5
        self.menu_item_name = "Sync Examples"

    def target_field_content(self, sub_dict):
        """ Takes a subset of self.data and transforms it to
        the string to be written in the field self.targetField."""
        out = unicode("")
        for key in sub_dict.keys():
            # todo: better to use enumerate and then abort; like this it's hard to read
            for i in range(min(self.max_examples, len(sub_dict[key][self.source_fields[0]]))):
                out += highlight_match(sub_dict[key][self.source_fields[0]][i].strip(), key)
                # todo: better use function format_meaning
                meaning = sub_dict[key][self.source_fields[1]][i].strip()
                # clean = case insensitive replace of list members with some string
                meaning = clean(meaning, ['\n', '<br>', '</div>', '</p>', ','], '; ')
                meaning = clean(meaning, ['<div>' ], '')
                meaning = clean(meaning, ['&nbsp;'], ' ')
                # only one meaning:
                meaning = meaning.split(';')[0]
                if meaning[:3] == '1. ':
                    meaning = meaning[3:]
                deck = unicode(self.deck_tag_dict[sub_dict[key]["__DECK__"][i]])
                out += " (%s) [%s]<br>" % (meaning.strip(), deck)
        # split last <br>
        return out[:-4]

    def add_note_to_db(self, note, deck):
        # todo: Probably smart to change the structure to
        # { kanji1: [ {souurceFieldName: Value} ] }
        # self.data looks like this:
        # { kanji1 : { sourceField1Name : [ sourceFieldValue1, sourceFieldValue2, ...] },
        #            { sourceField2Name : [ sourceFieldValue1, sourceFieldValue2, ...] }
        #   kanji2 : ... }
        # where sourceFieldValue1, sourceFieldValue2 etc. belong to the same source note.

        # loop over all kanjis that are found in the sourceMatch field of the source note
        for kanji in get_kanjis(note[self.source_match]):

                # todo: can't we just take a defaultdict?
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
                    # fixme: does it make any sense to update?
                    # todo: just use append all. If there are duplicates, it's the users fault.
                    # soruceFieldValue (Reading of a word) already in database
                    # only update
                    # index of that specific sourceFieldValue in the database
                    index = self.data[kanji][self.source_fields[0]].index(note[self.source_fields[0]])
                    # update meaning of the word.....
                    self.data[kanji][self.source_fields[1]][index] = note[self.source_fields[1]]
                else:
                    # append all
                    for sourceField in self.source_fields:
                        self.data[kanji][sourceField].append(note[sourceField])

                # doing the same thing with the deck value
                # todo: just use default dict
                if "__DECK__" not in self.data[kanji]:
                    self.data[kanji]["__DECK__"] = [deck]
                else:
                    self.data[kanji]["__DECK__"].append(deck)