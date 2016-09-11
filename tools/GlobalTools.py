#coding: utf-8

import sqlite3
import win32api
import StringIO
import unicodedata
from PyQt4 import QtCore
import sys
import Database

def is_exe():
	return hasattr(sys, "frozen")

# Need to know the supported charaters for Consolas for text alignment
supportedUnicode=[]
if is_exe():
	for str in win32api.LoadResource(0, u'SUPPORTEDUNICODE_TXT', 3).split('\n') :
		supportedUnicode.append(int(str,16))
else:
	file=open('SupportedUnicode.txt','r')
	for str in file.read().split('\n') :
		supportedUnicode.append(int(str,16))
	file.close()

# convert special entities for html
# not sure if there's other entity to handle?
def convertHTMLEntities(str):
	return str.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('\"','&quot;')

# Define the width of a character
def strWidth(str):
	width=0
	for ch in unicode(str):
		status = unicodedata.east_asian_width(ch)
		if status=='W' or status=='F' : width+=2
		elif status=='A' :
			if ord(ch) in supportedUnicode : width+=1
			else: width+=2
		else: width+=1
	return width

# Truncate the string into 34 width
def strTruncateTo34(str):
	width=0
	result=''
	for ch in unicode(str):
		status = unicodedata.east_asian_width(ch)
		if status=='W' or status=='F' : width+=2
		elif status=='A' :
			if ord(ch) in supportedUnicode : width+=1
			else: width+=2
		else: width+=1
		result+=ch
		if width==32:
			result+='..'
			break
		if width==33:
			result+='.'
			break
	return result

# global logger: redirect message to QT
class Logger(QtCore.QObject):
	signalWrite = QtCore.pyqtSignal(object,object)
	signalClear = QtCore.pyqtSignal()
	def write(self,string):
		self.signalWrite.emit(string,True)
	def writeCurrentLine(self,string):
		self.signalWrite.emit(string,False)
	def clear(self):
		self.signalClear.emit()
logger=Logger()


# function: view database status
def printDatabaseStatus():
	with Database.lock:
		conn = sqlite3.connect(Database.path)
		conn.row_factory = sqlite3.Row
		cur = conn.cursor()
		cur.execute('''
			SELECT COUNT(*) AS cnt FROM rivals
		''')
		rn=cur.fetchall()[0]['cnt']
		cur.execute('''
			SELECT COUNT(*) AS cnt FROM scores
		''')
		sn=cur.fetchall()[0]['cnt']
		cur.execute('''
			SELECT id,name FROM rivals WHERE active=2
		''')
		players=cur.fetchall()
		conn.close()
		
		logger.write( '-------- Database status ---------\n' )
		logger.write( ' The database contains:           \n' )
		logger.write( '                   <font\tstyle="color:LightGray">%8d</font> rivals\n'%rn )
		logger.write( '                   <font\tstyle="color:LightGray">%8d</font> scores\n'%sn )
		logger.write( ' Current player:                  \n' )
		if not players:
			logger.write( '                              None\n' )
		for player in players:
			playerMessage='<font\tstyle="color:Khaki">%6d %s</font>'%(player['id'],player['name'])
			leftPad=''
			width=7+strWidth(player['name'])
			if width<34 : leftPad=' '*(34-width)
			logger.write( leftPad+playerMessage+'\n' )
		logger.write( '----------------------------------\n' )
		logger.write( '\n' )
		
		

def printHelloMessage():
	with Database.lock:
		
		logger.clear()
		logger.write( '--- LR2 Rival Ranking commands ---\n' )
		logger.write( '  <font\tstyle="color:LightGray">F1</font> - About LR2 Rival Ranking    \n' )
		logger.write( '  <font\tstyle="color:LightGray">F2</font> - Modify Ir/ data in LR2     \n' )
		logger.write( '  <font\tstyle="color:LightGray">F3</font> - View database status       \n' )
		logger.write( '  <font\tstyle="color:LightGray">F4</font> - Reset log                  \n' )
		logger.write( '----------------------------------\n' )
		logger.write( '\n' )
		
		
