#coding: utf-8
import sqlite3
import win32api
from httplib import HTTPMessage
from StringIO import StringIO
import unicodedata
from PyQt4 import QtCore
import sys
import os
import threading

# Need to know the supported charaters for Consolas for text alignment
supportedUnicode=[]

def is_exe(): return hasattr(sys, "frozen")

# convert special entities for html
def convertHTMLEntities(str):
	return str.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

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

# a simple fake response for the generated result
class SimpleHTTPResponse():
	def __init__(self):
		self.msg = HTTPMessage(StringIO())
		self.msg['content-type'] = 'text/plain'
		self.status = 200
		self.reason = 'OK'

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

# for sqlite and qt logger with multithreads
lock = threading.Lock()

misc={}
dbdir=''
dbpath=''


def init(version):
	global supportedUnicode,lock,misc,dbdir,dbpath
	
	if is_exe():
		for str in win32api.LoadResource(0, u'SUPPORTEDUNICODE_TXT', 3).split('\n') :
			supportedUnicode.append(int(str,16))
	else:
		file=open('SupportedUnicode.txt','r')
		for str in file.read().split('\n') :
			supportedUnicode.append(int(str,16))
		file.close()
	
	# init database
	dbdir = '%s\\LR2RR\\' %  os.environ['APPDATA'] 
	if not os.path.exists(dbdir):
		os.makedirs(dbdir)
	dbpath = '%sdata.db' % dbdir
	with lock:
		conn = sqlite3.connect(dbpath)
		conn.row_factory = sqlite3.Row
		cur = conn.cursor()
		try:
			cur.execute('''
				CREATE TABLE IF NOT EXISTS
				rivals(
					id INTEGER NOT NULL UNIQUE,
					name TEXT,
					lastupdate INTEGER NOT NULL,
					active INTEGER
				)''')
			cur.execute('''
				CREATE TABLE IF NOT EXISTS
				scores(
					hash TEXT NOT NULL,
					id INTEGER NOT NULL,
					clear INTEGER NOT NULL,
					notes INTEGER NOT NULL,
					combo INTEGER NOT NULL,
					pg INTEGER NOT NULL,
					gr INTEGER NOT NULL,
					minbp INTEGER NOT NULL,
					UNIQUE(hash, id)
				)''')
			cur.execute('''
				CREATE TABLE IF NOT EXISTS
				misc(
					key TEXT NOT NULL UNIQUE,
					value TEXT
				)''')
			cur.execute('''
				REPLACE INTO misc VALUES('version',?)
			''',(version,))
			cur.execute('''
				INSERT OR IGNORE INTO misc VALUES('lr2exepath','')
			''')
			cur.execute('''
				INSERT OR IGNORE INTO misc VALUES('webpageextension','False')
			''')
			conn.commit()
		except:
			conn.rollback()
			sys.exit()
		cur.execute('SELECT * FROM misc')
		temp=cur.fetchall()
		for tt in temp:
			misc[tt['key']]=tt['value']
		conn.close()