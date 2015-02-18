#!/usr/bin/env python
import re
# import the main window object (mw) from ankiqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo
# import all of the Qt GUI library
from aqt.qt import *
from anki.hooks import addHook


def getKanjis(string):
		return re.findall(ur'[\u4e00-\u9fbf]',string)

class readingSync(object):
	# There are 2 methods for syncing the readings
	# 1. Loop through the deck with the readings and 
	#    sync everything
	# 2. Look for the kanjis of one new card and sync this one only
	#    (slow in comparison with 1, but faster if only applied to one card)
	def __init__(self):
		# We sync from sourceDecks to targetDecks
		# Note that if you have sutargetDecks, e.g. a subdeck rtk2
		# to the deck KANJI, then the name of the deck is KANJI::rtk2
		self.sourceDecks=["KANJI::rtk2","KANJI::readings"]
		self.targetDecks=["VOCAB::vocabular_main","VOCAB::vocab_new"]
		# For the automated completion of fields checks 
		# for the card type instead:
		self.sourceCards=['readings']
		self.targetCards='myJapanese_example_sentences'[]
		# Compare the following fields from source and target
		self.sourceMatch='Expression'
		self.targetMatch='Expression'
		# Take data from field sourceField and write it to targetField
		self.sourceFields=['story','kanji_examples']
		self.targetField='readings_story'
		# For the first method, we will store all data here.
		self.data={}

	def setupMenu(self,browser):
		a = QAction("Sync Reading Stories",browser)
		browser.form.menuEdit.addAction(a)
		browser.connect(a, SIGNAL("triggered()"), self.syncAll)

	def buildData(self):
		""" Build self.data """
		# loop through sourceDeck and build self.data
		nids=[]
		self.data={}
		for deck in self.sourceDecks:
			nids+=mw.col.findCards("deck:%s" % deck)
		for nid in nids:
			card=mw.col.getCard(nid)
			note = card.note()
			self.dataNote(note)

	def dataNote(self,note):
		for kanji in getKanjis(note[self.sourceMatch]):
				self.data[kanji]={}
				for sourceField in self.sourceFields:
					self.data[kanji][sourceField]=note[sourceField]

	def joinSourceFields(self,subDict):
		""" Takes a subset of self.data and transforms it to 
		the string to be written in the field self.targetField."""
		out=unicode("")
		for key in subDict.keys():
			out+='<span style="color:red">'+key+'</span>: '
			if subDict[key][self.sourceFields[0]].strip():
				out+=subDict[key][self.sourceFields[0]].strip()
			if subDict[key][self.sourceFields[1]].strip():
				out+="Ex.: "+subDict[key][self.sourceFields[1]].strip()
			out+="<br>"
		# split last <br>
		return out[:-4]

	def syncAll(self):
		self.buildData()
		# get all note ids that should be updated
		nids=[]
		for deck in self.targetDecks:
			nids+=mw.col.findCards("deck:%s" % deck)
		# loop over them
		for nid in nids:
			card=mw.col.getCard(nid)
			note=card.note()
			self.syncSingleTarget(note)
	
	def syncSingleTarget(self,note):
		if self.data=={}:
			# self.data has not been initialized
			self.buildData()
		kanjis=getKanjis(note[self.sourceMatch])
		subDict={}
		for kanji in kanjis:
			if kanji in self.data.keys():
				subDict[kanji]=self.data[kanji]
		note[self.targetField]=self.joinSourceFields(subDict)
		note.flush() # don't forget!
		print(note[self.targetField])
	
	def onFocusLost(self,flag,note,field):
		""" this method gets called as soon as somebody 
		edits a field on a card, i.e. we use it to automatically update 
		the target field accordingly. See http://ankisrs.net/docs/addons.html#hooks """
		# first we check if this is a card
		# we're interested in:
		# Case 1: 	Somebody changes something in sourceDeck
		# 			then we update self.data (but don't sync automatically)
		# Case 2:	Somebody changes something in targetDeck
		#			then we sync
		# whenever a card is irrelevant, we return $flag
		print('trigger')
		deck=mw.col.decks.current()['name']
		print(deck)
		if deck in self.sourceDecks:
			# here we react only, if one of the sourceFields
			# from which we extract Information is changed
			# this is enugh to handle cases of a new kanji-reading
			# added.
			srcFields=self.sourceFields
			ok=False
			for c, name in enumerate(mw.col.models.fieldNames(note.model())):
				for f in srcFields:
					if name == f:
						if field==c:
							ok=True
			if not ok:
				return flag
			self.dataNote(note)
			return True
		elif deck in self.targetDecks:
			print('target')
			srcFields=self.targetMatch
			for c, name in enumerate(mw.col.models.fieldNames(note.model())):
				for f in srcFields:
					if name == f:
						src = f
						srcIdx = c
			if field != srcIdx:
				return flag
			print('sync')
			self.syncSingleTarget(note)
			return True
		else:
			return flag

a=readingSync()
addHook('browser.setupMenus',a.setupMenu)
addHook('editFocusLost', a.onFocusLost)
