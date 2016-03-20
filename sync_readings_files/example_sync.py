#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .sync import Sync
from .util import ci_list_replace

# Adds words which contain a certain kanji to the 'kanji_examples' field
# of the readings deck


class ExampleSync(Sync):
    """

    """
    def __init__(self):
        super(ExampleSync, self).__init__()

        self.source_decks = ["VOCAB::vocabular_main",
                             "VOCAB::vocab_new",
                             "VOCAB::vocab_kanji1000",
                             "VOCAB::vocab_saikin"]
        self.source_card_names = ['myJapanese_example_sentences',
                                  'myJapanese_reverse']
        self.source_kanji_field = 'Expression'
        self.source_harvest_fields = ['Reading', 'Meaning']
        # note: also adapt the method format_target_field_content accordingly!

        self.target_decks = ["KANJI::readings"]
        self.target_card_names = ['readings']
        self.target_kanji_field = 'Expression'
        self.target_target_field = 'kanji_examples'
        # import note: CONTENTS OF THIS FIELD WILL BE OVERWRITTEN

        self.menu_item_name = "Sync Examples"

        # Other properties
        self.max_examples = 5

    def format_target_field_content(self, db_subset):
        """ Takes a subset of self.db and returns
        the string to be written in the field self.target_target_field.
        :type db_subset: Db
        """
        out = unicode("")
        for kanji in db_subset.keys():
            for db_entry in db_subset[kanji][:self.max_examples]:
                word = self.format_word(db_entry['Reading'], kanji)
                meaning = self.format_meaning(db_entry['Meaning'])
                deck_tag = self.format_deck(db_entry["__DECK__"])
                out += "%s%s%s<br>" % (word, meaning, deck_tag)
        # delete last <br>
        return out[:-4]

    @staticmethod
    def format_deck(deck):
        """ For format_target_field_content: Format deck variable.
        :type deck: str
        """
        deck_tag_dict = {"VOCAB::vocabular_main": u"本",
                         "VOCAB::vocab_new": u"新",
                         "VOCAB::vocab_saikin": u"最",
                         "VOCAB::vocab_kanji1000": u"漢",
                         "": u"無"}
        if deck in deck_tag_dict:
            deck_tag = unicode(deck_tag_dict[deck])
        else:
            deck_tag = deck
        if deck_tag:
            return u" [%s]" % deck_tag
        else:
            # maybe called with empty deck variable
            return deck_tag

    @staticmethod
    def format_word(word, kanji=""):
        """ For format_target_field_content: Format word.
        :type word: str
        :type kanji: str
        """
        word = word.strip()
        # highlight the occurrence of the kanji in red
        return word.replace(kanji, '<span style="color:red">%s</span>' % kanji)

    @staticmethod
    def format_meaning(meaning):
        """ For format_target_field_content: Format meaning of word.
        :type meaning: str
        """
        meaning = meaning.strip()
        print meaning
        # 1. replace unwanted html members.
        # Also we want to split separate meanings later, so replace all characters probably
        # separating separate meanings by by ','
        meaning = ci_list_replace(meaning, ['\n', '<br>', '</div>', '</p>', ','], '; ')
        print meaning

        meaning = ci_list_replace(meaning, ['<div>', '<p>'], '')
        print meaning

        meaning = ci_list_replace(meaning, ['&nbsp;'], ' ')
        print meaning

        meaning = ci_list_replace(meaning, [';', ','], ',')
        # 2. if there are multiple meanings, only take the first one:
        meaning = meaning.split(';')[0]
        print meaning

        # 3. Split formatting characters
        if meaning.startswith('1. '):
            meaning = meaning[3:].strip()
        # 4. Bring in final format.
        if meaning:
            return " (%s) " % meaning
        else:
            return ""
