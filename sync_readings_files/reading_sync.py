#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .sync import Sync
from .util import ci_list_replace, ci_list_replace_trailing

# todo: move to docstring
# adds the story etc. of the readings to the field 'readings_story'
# of the vocabulary notes.


class ReadingsSync(Sync):
    """
    """
    def __init__(self):
        """Mostly configuration stuff."""
        super(ReadingsSync, self).__init__()
        # Sync super class after we set all the properties!
        # (allows checks to be run on below settings)

        self.source_decks = ["KANJI::readings"]
        self.source_cards = ['readings']
        self.source_kanji_field = 'Expression'
        self.source_harvest_fields = ['onyomi_story', 'kunyomi_story', 'combined_story']
        # note: also adapt the method format_target_field_content accordingly!

        self.target_decks = ["VOCAB::vocabular_main",
                             "VOCAB::vocab_new",
                             "VOCAB::vocab_kanji1000",
                             "VOCAB::vocab_saikin"]
        self.target_cards = ['myJapanese_example_sentences']
        self.target_kanji_field = 'Expression'
        self.target_target_field = 'readings_story'

        self.menu_item_name = "Sync Reading stories"



    def format_target_field_content(self, db_subset):
        """ Takes a subset of self.data and transforms it to
        the string to be written in the field self.targetField."""
        out = unicode("")
        for kanji in db_subset.keys():
            for db_entry in db_subset[kanji]:
                on = db_entry['onyomi_story']
                kun = db_entry['kunyomi_story']
                comb = db_entry['combined_story']
                ex = db_entry['kanji_examples']
                print on, kun, comb
                out += '<span style="color:red">%s</span>: ' % kanji
                if on:
                    out += "O: %s" % on.strip()
                if kun:
                    out += "K: %s" % kun.strip()
                if comb:
                    out += "C: %s" % comb.strip()
                out += "<br>"  # compensate for last <br> later
        # split last <br>s
        out = ci_list_replace_trailing(out, ["<br>", "<p>"], "")
        return out
