#coding: utf-8

from PyQt4 import QtGui, QtCore
from StringIO import StringIO
import sys
import os
import win32api

import GlobalTools

class MainWindow(QtGui.QTextEdit):
	def __init__(self,original_hosts,version):
		QtGui.QTextEdit.__init__(self)
		
		self.original_hosts=original_hosts
		
		self.fontDB = QtGui.QFontDatabase()
		self.fontDB.addApplicationFontFromData(StringIO( win32api.LoadResource(0, u'CONSOLASHIGH_TTF', 2)).getvalue())
		# self.fontDB.addApplicationFont('ConsolasHigh.ttf')
		self.setStyleSheet('''
			font-size: 10pt;
			font-family: ConsolasHigh,"MS Gothic";
			background-color:rgb(20,20,20);
			color: rgb(150,150,150);
		''')
		
		
		img=QtGui.QPixmap()
		img.loadFromData(StringIO( win32api.LoadResource(0, u'CLOUD_PNG', 1)).getvalue())
		self.setWindowIcon(QtGui.QIcon( img ))
		# self.setWindowIcon(QtGui.QIcon( 'cloud.png' ))
		
		self.setReadOnly(True)
		self.setWindowTitle(' LR2 Rival Ranking | v'+version)
		self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint)
		
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
		
		# to keep the log contents
		self.line_n=0
		self.lines=['']*150
		
		GlobalTools.logger.signal.connect(self.updateLog)
		sys.stderr=sys.stdout
		
		
	def closeEvent(self, event):
		# recover original hosts contents
		file=open( os.environ['SystemRoot']+'\\System32\\drivers\\etc\\hosts','w')
		file.write(self.original_hosts)
		file.close()
		event.accept()
	def updateLog(self,string):
		# write sth to log
		
		# handle whitespace and \n
		self.lines[self.line_n]=string.replace(' ','&nbsp;').replace(u'　','&nbsp;&nbsp;').replace('\n','<br>')
		
		# only keep the latest 150 messages
		self.line_n=(self.line_n+1)%150
		self.setHtml(  ''.join(self.lines[self.line_n:])+''.join(self.lines[:self.line_n])  )
		sb = self.verticalScrollBar()
		sb.setValue(sb.maximum())



