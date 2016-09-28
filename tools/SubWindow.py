#coding: utf-8
from PyQt4 import QtGui, QtCore, QtWebKit
from StringIO import StringIO
import sys
import os
import win32api
import threading
import sqlite3

import GlobalTools
import IRFolderHandler

class HoverButton(QtGui.QPushButton):
	def __init__(self, text='', parent=None):
		QtGui.QPushButton.__init__(self, text, parent)
		self.setStyleSheet('border: 1px solid rgb(150,150,150);')
		self.setMouseTracking(True)

	def enterEvent(self, event):
		self.setStyleSheet('border: 1px solid LightGray;color: LightGray;')

	def leaveEvent(self, event):
		self.setStyleSheet('border: 1px solid rgb(150,150,150);')


class AboutWindow(QtGui.QDialog):
	def __init__(self,parent):
		QtGui.QDialog.__init__(self,parent)
		
		str=''
		str+='Thank you for using LR2 Rival Ranking!<br>'
		str+='Current version: <font style="color:LightGray">'+GlobalTools.version+'</font><br>'
		str+='<br>'
		str+='Author: <font style="color:LightGray">Leo Shen</font><br>'
		str+=u'LR2IR: <font style="color:LightGray">うまい焼鴨 (<a href="http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=mypage&playerid=121168" style="color:PowderBlue">121168</a>)</font><br>'
		str+='<br>'
		str+='Please visit our <a href="https://github.com/leoshen999/LR2RivalRanking" style="color:PowderBlue">GitHub page</a> for more information.'
		
		self.setFixedSize(380,160)
		self.setWindowTitle('About LR2 Rival Ranking')
		self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
		
		self.label=QtGui.QLabel(str,self)
		self.label.setOpenExternalLinks(True)
		self.label.setGeometry(10,10,360,140)

class ModifyIRWindow(QtGui.QDialog):
	def __init__(self,parent):
		QtGui.QDialog.__init__(self,parent)
		self.setFixedSize(310,180)
		self.setWindowTitle('Modify Ir/ data in LR2')
		self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
		
		conn = sqlite3.connect(GlobalTools.dbpath)
		conn.row_factory = sqlite3.Row
		cur = conn.cursor()
		cur.execute('''
			SELECT value FROM misc WHERE key='lr2exepath'
		''')
		path=cur.fetchall()[0]['value']
		conn.close()
		self.labelPath=QtGui.QLabel('LR2.exe location:',self)
		self.labelPath.setGeometry(10,10,120,25)
		self.lineEditPath=QtGui.QLineEdit(path,self)
		self.lineEditPath.setGeometry(30,36,200,23)
		self.lineEditPath.setStyleSheet('border: 1px solid rgb(150,150,150);')
		self.buttonBrowse=HoverButton('Browse',self)
		self.buttonBrowse.setGeometry(235,36,60,23)
		self.buttonBrowse.setStyleSheet('border: 1px solid rgb(150,150,150);')
		self.buttonBrowse.clicked.connect(self.selectFile)
		
		str ='<font style="color:Salmon"># Caution: This function may cost much<br>'
		str+='&nbsp;&nbsp;time and create lots of xml files in<br>'
		str+='&nbsp;&nbsp;the Ir/ folder.</font>'
		self.labelCaution=QtGui.QLabel(str,self)
		self.labelCaution.setGeometry(10,65,290,75)
		
		self.buttonOK=HoverButton('OK',self)
		self.buttonOK.setGeometry(160,141,60,23)
		self.buttonOK.clicked.connect(self.startModifyIRFolder)
		self.buttonOK.clicked.connect(self.close)
		
		self.buttonCancel=HoverButton('Cancel',self)
		self.buttonCancel.setGeometry(235,141,60,23)
		self.buttonCancel.clicked.connect(self.close)
		
	def selectFile(self):
		path=QtGui.QFileDialog.getOpenFileName(self,caption='Specify the location of LR2.exe',filter='Executable (*.exe)')
		if path:
			self.lineEditPath.setText(path)
	def startModifyIRFolder(self):
		path=unicode(self.lineEditPath.text().toUtf8(), encoding="utf_8")
		thr=threading.Thread(target=IRFolderHandler.modifyIRFolder,args=(path,))
		thr.daemon=True
		thr.start()