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

def highlightMatch(string,match,pre='<span style="color:red">',after='</span>'):
	out=""
	for letter in string:
		if letter!=match:
			out+=letter
		else:
			out+=pre+letter+after
	return out

class readingSync(object):
	def __init__(self):
		# We sync from sourceDecks to targetDecks
		# Note that if you have sutargetDecks, e.g. a subdeck rtk2
		# to the deck KANJI, then the name of the deck is KANJI::rtk2
		self.sourceDecks=["KANJI::rtk2","KANJI::readings"]
		self.targetDecks=["VOCAB::vocabular_main","VOCAB::vocab_new"]
		# For the automated completion of fields checks 
		# for the card type instead:
		self.sourceCards=['readings']
		self.targetCards=['myJapanese_example_sentences']
		# Compare the following fields from source and target
		self.sourceMatch='Expression'
		self.targetMatch='Expression'
		# Take data from field sourceField and write it to targetField
		self.sourceFields=['story','kanji_examples']
		self.targetField='readings_story'
		# For the first method, we will store all data here.
		self.data={}
	
	def joinSourceFields(self,subDict):
		""" Takes a subset of self.data and transforms it to 
		the string to be written in the field self.targetField."""
		out=unicode("")
		for key in subDict.keys():
			out+='<span style="color:red">'+key+'</span>: '
			if subDict[key][self.sourceFields[0]].strip():
				out+=subDict[key][self.sourceFields[0]].strip()
			if subDict[key][self.sourceFields[1]].strip():
				out+=" Ex.: <br>"+subDict[key][self.sourceFields[1]].strip()+"<br>"
			out+="<br>"
		# split last <br>s
		if out[:-8]=="<br><br>":
			return out[:-8]
		else:
			return out[:-4]

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
			self.datafySingleNote(note)

	def datafySingleNote(self,note):
		for kanji in getKanjis(note[self.sourceMatch]):
				self.data[kanji]={}
				for sourceField in self.sourceFields:
					self.data[kanji][sourceField]=note[sourceField]

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
	
	def onFocusLost(self,flag,note,field):
		""" this method gets called as soon as somebody 
		edits a field on a card, i.e. we use it to automatically update 
		the target field accordingly. See http://ankisrs.net/docs/addons.html#hooks """
		# first we check if this is a card
		# we're interested in:
		# Case 1: 	Somebody changes something in sourceModel
		# 			then we update self.data (but don't sync automatically)
		# Case 2:	Somebody changes something in targetModel
		#			then we sync
		# whenever a card is irrelevant, we return $flag
		model=note.model()['name']
		if model in self.sourceCards:
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
			self.datafySingleNote(note)
			return True
		elif model in self.targetCards:
			srcFields=[self.targetMatch]
			ok=False
			for c, name in enumerate(mw.col.models.fieldNames(note.model())):
				for f in srcFields:
					if name == f:
						if field==c:
							ok=True
			if not ok:
				return flag
			self.syncSingleTarget(note)
			return True
		else:
			return flag

class exampleSync(readingSync):
	def __init__(self):
		super(exampleSync,self).__init__()
		self.targetDecks=["KANJI::rtk2","KANJI::readings"]
		self.sourceDecks=["VOCAB::vocabular_main","VOCAB::vocab_new"]
		self.targetCards=['readings']
		self.sourceCards=['myJapanese_example_sentences']
		self.sourceMatch='Expression'
		self.targetMatch='Expression'
		self.sourceFields=['Expression','Meaning']
		self.targetField='kanji_examples'
	def setupMenu(self,browser):
		a = QAction("Sync Examples",browser)
		browser.form.menuEdit.addAction(a)
		browser.connect(a, SIGNAL("triggered()"), self.syncAll)
	def joinSourceFields(self,subDict):
		""" Takes a subset of self.data and transforms it to 
		the string to be written in the field self.targetField."""
		out=unicode("")
		for key in subDict.keys():
			for i in range(len(subDict[key][self.sourceFields[0]])):
				out+=highlightMatch(subDict[key][self.sourceFields[0]][i].strip(),key)
				out+=" (%s)" % subDict[key][self.sourceFields[1]][i].strip().replace('\n','; ').replace('<br>','; ')[:30]
				out+="<br>"
		# split last <br>
		return out[:-4]
	def datafySingleNote(self,note):
		for kanji in getKanjis(note[self.sourceMatch]):
				if not kanji in self.data:
					self.data[kanji]={}
				for sourceField in self.sourceFields:
					if not sourceField in self.data[kanji]:
						self.data[kanji][sourceField]=[note[sourceField]]
					else:
						self.data[kanji][sourceField].append(note[sourceField])

a=readingSync()
b=exampleSync()
addHook('browser.setupMenus',a.setupMenu)
addHook('browser.setupMenus',b.setupMenu)
addHook('editFocusLost', a.onFocusLost)
addHook('editFocusLost', b.onFocusLost)
