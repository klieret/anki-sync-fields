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
		mw.progress.start()
		for deck in self.sourceDecks:
			nids+=mw.col.findCards("deck:%s" % deck)
		for nid in nids:
			card=mw.col.getCard(nid)
			note = card.note()
			for kanji in getKanjis(note[self.sourceMatch]):
				self.data[kanji]={}
				for sourceField in self.sourceFields:
					self.data[kanji][sourceField]=note[sourceField]
		mw.progress.finish()
		mw.reset()

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
		kanjis=getKanjis(note[self.sourceMatch])
		subDict={}
		for kanji in kanjis:
			if kanji in self.data.keys():
				subDict[kanji]=self.data[kanji]
		note[self.targetField]=self.joinSourceFields(subDict)
		note.flush() # don't forget!
	
	def slowMethod(self,kanji):
		# get note ids of relevant notes
		nids=[]
		for deck in self.sourceDecks:
			# just use the standard search of anki
			# i.e. search for deck:sourceDeck sourceMatch:kanji
			nids+=mw.col.findCards("deck:%s %s:%s" % (deck, self.sourceMatch, kanji))
		out=unicode("")
		for nid in nids:
			note=mw.col.getCard(nid).note()
			
			out+=note[self.sourceField1].strip()
			if note[self.sourceField2].strip():
				out+="Ex.: "
				out+=note[self.sourceField2].strip()
		return out
	
	

a=readingSync()
addHook('browser.setupMenus',a.setupMenu)

