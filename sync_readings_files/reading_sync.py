#!/usr/bin/env python
# -*- coding: utf-8 -*-

from anki.utils import stripHTML
from .sync import Sync
from .util import ci_list_replace_trailing

# todo: move to docstring
# adds the story etc. of the readings to the field 'readings_story'
# of the vocabulary notes.


class ReadingsSync(Sync):
    def __init__(self):
        """Mostly configuration stuff."""
        super(ReadingsSync, self).__init__()

        self.source_decks = ["KANJI::readings"]
        self.source_card_names = ['readings']
        self.source_kanji_field = 'Expression'
        self.source_harvest_fields = ['onyomi_story', 'kunyomi_story', 'combined_story']
        # note: also adapt the method format_target_field_content accordingly!

        self.target_decks = ["VOCAB::vocabular_main",
                             "VOCAB::vocab_new",
                             "VOCAB::vocab_kanji1000",
                             "VOCAB::vocab_saikin",
                             "VOCAB::vocab_back"]
        self.target_card_names = ['myJapanese_example_sentences',
                                  'myJapanese_example_sentences_reverse_only']
        self.target_kanji_field = 'Expression'
        self.target_target_field = 'readings_story'

        self.menu_item_name = "Sync Reading stories"

    # todo: use stripHTML from Anki to check if string is empty
    def format_target_field_content(self, db_subset, fancy=True):
        """ Takes a subset of self.data and transforms it to
        the string to be written in the field self.targetField.
        @type db_subset: Db
        @param fancy: Use fancy layout
        """
        out = unicode("")
        if fancy:
            badge_attributes = ["border-radius: 25px",
                                "white-space: nowrap",
                                "display: inline",
                                "display: inline-block",
                                "padding-left: 8px",
                                "padding-right: 8px",
                                "border-color: black",
                                "background-color: yellow;"]
        else:
            badge_attributes = ["color: red"]
        badge_style = "; ".join(badge_attributes)

        for kanji in db_subset.keys():
            for db_entry in db_subset[kanji]:
                on = stripHTML(db_entry['onyomi_story']).strip()
                kun = stripHTML(db_entry['kunyomi_story']).strip()
                comb = stripHTML(db_entry['combined_story']).strip()
                out += u'<span style="{}">{}</span> '.format(badge_style, kanji)
                if on:
                    out += u"音: {}".format(on)
                if kun:
                    out += u"訓: {}".format(kun)
                if comb:
                    out += u"両: {}".format(comb)
                out += u"<br>"  # compensate for last <br> later
        # split last <br>s
        out = ci_list_replace_trailing(out, [u"<br>", u"<p>"], "")
        return out
