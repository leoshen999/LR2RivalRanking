#coding: utf-8
import sqlite3
import win32api
from PyQt4 import QtGui,QtCore
from httplib import HTTPMessage
from StringIO import StringIO
import sys
import os
import threading

def is_exe(): return hasattr(sys, "frozen")

# convert special entities for html
def convertHTMLEntities(str):
	return str.replace('<','&lt;').replace('>','&gt;').replace('"','&quot;').replace('\'','&#39;')
	# how about .replace('&','&amp;') ????

class SimpleHTTPResponse():
	def __init__(self):
		self.msg = HTTPMessage(StringIO())
		self.msg['content-type'] = 'text/plain'
		self.status = 200
		self.reason = 'OK'
class FailedHTTPResponse():
	def __init__(self):
		self.msg = HTTPMessage(StringIO())
		self.msg['content-type'] = 'text/plain'
		self.status = 400
		self.reason = 'Bad Request'

table_info={
	'normal_no2':[u'▽第2通常難易度','http://rattoto10.jounin.jp/table.html'],
	'insane_no2':[u'▼第2発狂難易度','http://rattoto10.jounin.jp/table_insane.html'],
	'normal':[u'☆通常難易度表','http://www.ribbit.xyz/bms/tables/normal.html'],
	'insane':[u'★発狂BMS難易度表','http://www.ribbit.xyz/bms/tables/insane.html'],
	'overjoy':[u'★★Overjoy','http://www.ribbit.xyz/bms/tables/overjoy.html'],
	'ln':[u'◆LN難易度','http://flowermaster.web.fc2.com/lrnanido/gla/LN.html']}
dbLock = threading.Lock()
logLock = threading.Lock()

class Logger(QtCore.QObject):
	signalWrite = QtCore.pyqtSignal(object,object)
	signalWriteIrLastupdate = QtCore.pyqtSignal(object)
	signalWriteDifficultiesLastupdate = QtCore.pyqtSignal(object)
	def write(self,string,newLine=True):
		self.signalWrite.emit(string,newLine)
	def writeIrLastupdate(self,string):
		self.signalWriteIrLastupdate.emit(string)
	def writeDifficultiesLastupdate(self,string):
		self.signalWriteDifficultiesLastupdate.emit(string)
logger=Logger()

mainWindow=''

dbdir=''
conn = ''
cur = ''
misc={}

webstyle=''
webscript=''
windowIcon=''
styleSheet=''

def init(version):
	global dbdir,conn,cur,misc
	global webstyle,webscript
	global windowIcon,styleSheet
	
	styleSheet='''
		font-size: 10pt;
		font-family: ConsolasHigh,Meiryo;
		background-color: Black;
		color: DarkGray;
	'''
	if is_exe():
		img=QtGui.QPixmap()
		img.loadFromData(StringIO( win32api.LoadResource(0, u'CLOUD_PNG', 1)).getvalue())
		windowIcon=QtGui.QIcon( img )
		webstyle= win32api.LoadResource(0, u'STYLE_CSS', 2)
		webscript= win32api.LoadResource(0, u'SRC_JS', 3)
		QtGui.QFontDatabase().addApplicationFontFromData(StringIO( win32api.LoadResource(0, u'CONSOLASHIGH_TTF', 4)).getvalue())
	else:
		windowIcon=QtGui.QIcon( 'resources/cloud.png' )
		with open('resources/style.css','r') as fp: webstyle=fp.read()
		with open('resources/src.js','r') as fp: webscript=fp.read()
		QtGui.QFontDatabase().addApplicationFont('resources/ConsolasHigh.ttf')
	
	# init database
	dbdir = '%s\\LR2RR\\' %  os.environ['APPDATA']
	if not os.path.exists(dbdir):
		os.makedirs(dbdir)
	conn = sqlite3.connect(dbdir+'data.db',check_same_thread=False)
	conn.row_factory = sqlite3.Row
	cur = conn.cursor()
	with dbLock:
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
				recent(
					hash TEXT NOT NULL,
					id INTEGER NOT NULL,
					title TEXT,
					lastupdate INTEGER NOT NULL,
					UNIQUE(hash, id)
				)''')
			cur.execute('''
				CREATE TABLE IF NOT EXISTS
				misc(
					key TEXT NOT NULL UNIQUE,
					value TEXT
				)''')
			cur.execute('REPLACE INTO misc VALUES("version",?)',(version,))
			cur.execute('INSERT OR IGNORE INTO misc VALUES("lr2exepath","")')
			cur.execute('INSERT OR IGNORE INTO misc VALUES("irlastupdate","Never")')
			cur.execute('INSERT OR IGNORE INTO misc VALUES("difficultieslastupdate","Never")')
			conn.commit()
			cur.execute('SELECT * FROM misc')
			for tt in cur.fetchall(): misc[tt['key']]=tt['value']
		except:
			conn.rollback()
			sys.exit()