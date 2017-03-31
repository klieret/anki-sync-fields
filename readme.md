# Syncing fields between Anki notes.

Plugin for [Anki](https://apps.ankiweb.net/), a spaced repetition flashcard program. Some basics: [Anki manual](https://apps.ankiweb.net/docs/manual.html#the-basics).

**This Addon requires substantial configuration/adaptation to work for you. Rudimentary knowledge of python will be helpful. Note that the *target fields* of the *target notes* will be overwritten, so please be careful!**

## Use case

This plugin was designed for the following scenario: When learning Japanese, one usually deals with at least two different kinds of notes/decks:

1. One for the Chinese characters ([Kanji](https://en.wikipedia.org/wiki/Kanji)), containing information such as meaning, reading (pronounciation) and mnemotics for each of them
2. One for vocabulary words which are written with Kana (syllable symbols) Kanji (a word can be written with none, or more than one Kanji, see [wiki: Japanese writing system](https://en.wikipedia.org/wiki/Japanese_writing_system))

This addon exchanges information between both sets of notes:

1. Kanji → Vocabulary: Adds information about the kanji that are used in the writing of the word to a new field of the vocabulary note
2. Vocabulary → Kanji: Adds exampless of (already learned) words that use this kanji in its writing to a new field of the kanji note

## Implemented example

1. Kanji → Vocabulary: The word ```不思議```, read ふしぎ (fushigi) is written with three kanji ```不```, ```思```, and ```議```. All three kanji are found in the deck for kanji readings, and mnemotics for the [onyomi](https://en.wikipedia.org/wiki/Kanji#On.27yomi_.28Sino-Japanese_reading.29) of ```思```, and ```議``` were found. Those were written to the field in row ```O``` by this plugin (prefixed with ```音``` for Onyomi, ```音読み```). The examples in the ```X``` row are generated by Anki's Japanese plugin. 

    ![kanji2vocab_cropped](https://cloud.githubusercontent.com/assets/13602468/24543107/963a8674-15fe-11e7-8576-3ba48af47fbd.png)

2. Vocabylary → Kanji. My reading card of the kanji ```議```. First of all this was one of the notes whose information was transferred to the note ```不思議``` (the mnemotic for its reading was copied). 
   In my vocabulary decks several already learned words with this kanji were found, e.g. ```会議```. These were written to the field in the row ```X``` by this plugin. The last symbol in square brackets (e.g. ```[本]```) stands for the vocabulary deck where the words were found.

    ![vocab2kanji_cropped](https://cloud.githubusercontent.com/assets/13602468/24543108/9643e322-15fe-11e7-8256-57df16dc1699.png) 

## Code overview

This project has the following structure:

    ├── sync_fields_files
    │   ├── __init__.py         <-- empty (so that this becomes a module)
    │   ├── run.py              <-- builds the two Sync objects and 
    │   │                           connects them to Anki via hooks
    │   ├── sync.py             <-- defines Sync base class
    │   ├── example_sync.py     <-- Defines subclass of Sync to sync vocabulary → kanji
    │   ├── reading_sync.py     <-- Defines subclass of Sync to sync kanji → vocabulary
    │   ├── util.py             <-- useful functions
    │   └── log.py              <-- sets up log
    └── sync_fields.py          <-- loads run

The top level file ```sync_fields.py``` loads the file ```run.py```, which builds an object of type ```ExampleSync``` and ```ReadingSync``` and connects them to Anki via hooks. Both classes are subclasses of the class ```Sync```, defined in ```sync.py```. The class ```Sync``` also contains the database that temporarily stores all information that is nescessary for the sync.

Almost all of the interesting code is already implemented in the ```Sync``` class, the subclasses only

1. Fill in all the parameters (which decks/notes are to be synced to which decks/notes) etc.
2. Implement the function ```format_target_field_content```, which formats the string that is written to the target field of a target note, based on the database entries that correspond that note's kanji's. 

## Debugging

This plugin will always save a log ```sync_readings.log```, which should be located in this plugin's directory (```sync_fields_files```). 

There is also a switch ```dump_database_after_full_loop = False``` in ```log.py```. If set to ```True```, the full database will be dumped as a string to the log file after ```Sync.loop_source_notes``` was called (i.e. after a full loop over all source notes was performed). This may however not perform well (which is why it is disabled by default).