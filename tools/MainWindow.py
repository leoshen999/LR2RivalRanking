#coding: utf-8

from PyQt4 import QtGui, QtCore
from StringIO import StringIO
import sys
import os
import win32api
import threading
import sqlite3

import SubWindow
import GlobalTools

def printDatabaseStatus():
	with GlobalTools.lock:
		conn = sqlite3.connect(GlobalTools.dbpath)
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
		
		GlobalTools.logger.write( '-------- Database status ---------\n' )
		GlobalTools.logger.write( ' The database contains:           \n' )
		GlobalTools.logger.write( '                   <font\tstyle="color:LightGray">%8d</font> rivals\n'%rn )
		GlobalTools.logger.write( '                   <font\tstyle="color:LightGray">%8d</font> scores\n'%sn )
		GlobalTools.logger.write( ' Current player:                  \n' )
		if not players:
			GlobalTools.logger.write( '                              None\n' )
		for player in players:
			url='http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=mypage&playerid=%d' % (player['id'])
			playerMessage='<a\thref="%s"\tstyle="color:Khaki;text-decoration:none">%6d %s</a>'%(url,player['id'],player['name'])
			leftPad=''
			width=7+GlobalTools.strWidth(player['name'])
			if width<34 : leftPad=' '*(34-width)
			GlobalTools.logger.write( leftPad+playerMessage+'\n' )
		GlobalTools.logger.write( '----------------------------------\n' )
		GlobalTools.logger.write( '\n' )
def printHelloMessage():
	with GlobalTools.lock:
		GlobalTools.logger.clear()
		GlobalTools.logger.write( '--- LR2 Rival Ranking commands ---\n' )
		GlobalTools.logger.write( '  <font\tstyle="color:LightGray">F1</font> : Extend webpage function    \n' )
		GlobalTools.logger.write( '  <font\tstyle="color:LightGray">F2</font> : Modify Ir/ data in LR2     \n' )
		GlobalTools.logger.write( '  <font\tstyle="color:LightGray">F3</font> : View database status       \n' )
		GlobalTools.logger.write( '  <font\tstyle="color:LightGray">F4</font> : Reset log                  \n' )
		GlobalTools.logger.write( '  <font\tstyle="color:LightGray">F5</font> : About LR2 Rival Ranking    \n' )
		GlobalTools.logger.write( '----------------------------------\n' )
		GlobalTools.logger.write( '\n' )


class MainWindow(QtGui.QTextBrowser):
	def __init__(self,original_hosts):
		QtGui.QTextBrowser.__init__(self)
		
		self.original_hosts=original_hosts
		
		self.fontDB = QtGui.QFontDatabase()
		if GlobalTools.is_exe():
			self.fontDB.addApplicationFontFromData(StringIO( win32api.LoadResource(0, u'CONSOLASHIGH_TTF', 2)).getvalue())
		else:
			self.fontDB.addApplicationFont('ConsolasHigh.ttf')
		self.setStyleSheet('''
			font-size: 10pt;
			font-family: ConsolasHigh,"MS Gothic";
			background-color:rgb(20,20,20);
			color: rgb(150,150,150);
		''')
		
		
		if GlobalTools.is_exe():
			img=QtGui.QPixmap()
			img.loadFromData(StringIO( win32api.LoadResource(0, u'CLOUD_PNG', 1)).getvalue())
			self.setWindowIcon(QtGui.QIcon( img ))
		else:
			self.setWindowIcon(QtGui.QIcon( 'cloud.png' ))
		
		self.setReadOnly(True)
		self.setWindowTitle(' LR2 Rival Ranking')
		self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
		self.setOpenExternalLinks(True)
		self.resize(260,400)
		self.setFixedWidth(260)
		self.setMinimumHeight(400)
		
		sb = self.verticalScrollBar()
		sb.setStyleSheet('''
			QScrollBar:vertical {
				border: none;
				background: rgb(32,32,32);
				width: 10px;
				margin: 0 0 0 0;
			}
			QScrollBar::handle:vertical {
				background: rgb(64,64,64);
			}
			QScrollBar::add-line:vertical {
				border: none;
				height: 0px;
			}
			QScrollBar::sub-line:vertical {
				border: none;
				height: 0px;
			}
			QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
				background: none;
			}
		''')
		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
		
		# to keep the log contents
		self.line_n=0
		self.lines=['']*150
		
		GlobalTools.logger.signalWrite.connect(self.writeLog)
		GlobalTools.logger.signalClear.connect(self.clearLog)
		sys.stderr=sys.stdout
		
		self.extendWebpageWindow=SubWindow.ExtendWebpageWindow(self)
		self.aboutWindow=SubWindow.AboutWindow(self)
		self.modifyIRWindow=SubWindow.ModifyIRWindow(self)
		
		printHelloMessage()
		
	def closeEvent(self, event):
		# recover original hosts contents
		file=open( os.environ['SystemRoot']+'\\System32\\drivers\\etc\\hosts','w')
		file.write(self.original_hosts)
		file.close()
		event.accept()
	def writeLog(self,string,newLine=True):
		# write sth to log
		
		# roll back one line if write to current line
		if not newLine:
			self.line_n=(self.line_n+149)%150
		
		# handle whitespace and \n
		self.lines[self.line_n]=string.replace(' ','&nbsp;').replace(u'　','&nbsp;&nbsp;').replace('\n','<br>')
		
		# only keep the latest 150 messages
		self.line_n=(self.line_n+1)%150
		self.setHtml(  ''.join(self.lines[self.line_n:])+''.join(self.lines[:self.line_n])  )
		sb = self.verticalScrollBar()
		sb.setValue(sb.maximum())
	def clearLog(self):
		# function: reset log
		self.line_n=0
		self.lines=['']*150
		self.setHtml(  ''.join(self.lines[self.line_n:])+''.join(self.lines[:self.line_n])  )
		sb = self.verticalScrollBar()
		sb.setValue(sb.maximum())
	def keyPressEvent(self, event):
		if event.key()==QtCore.Qt.Key_F1:
			self.extendWebpageWindow.show()
		elif event.key()==QtCore.Qt.Key_F2:
			self.modifyIRWindow.show()
		elif event.key()==QtCore.Qt.Key_F3:
			thr=threading.Thread(target=printDatabaseStatus)
			thr.daemon=True
			thr.start()
		elif event.key()==QtCore.Qt.Key_F4:
			thr=threading.Thread(target=printHelloMessage)
			thr.daemon=True
			thr.start()
		elif event.key()==QtCore.Qt.Key_F5:
			self.aboutWindow.show()

