#coding: utf-8
from PyQt4 import QtGui, QtCore,QtWebKit
from StringIO import StringIO
import sys
import os
import threading
import sqlite3
import webbrowser

import GlobalTools
import ModifyIrHandler
import UpdateDifficultiesHandler

class HoverButton(QtGui.QPushButton):
	def __init__(self, text='', parent=None):
		QtGui.QPushButton.__init__(self, text, parent)
		self.setStyleSheet('border: 1px solid DarkGray;')
		self.setMouseTracking(True)

	def enterEvent(self, event):
		self.setStyleSheet('border: 1px solid Gainsboro;color: Gainsboro;')

	def leaveEvent(self, event):
		self.setStyleSheet('border: 1px solid DarkGray;')


class AboutWindow(QtGui.QDialog):
	def __init__(self,parent=None):
		QtGui.QDialog.__init__(self,parent)
		self.setWindowTitle('About LR2 Rival Ranking')
		self.setWindowIcon(GlobalTools.windowIcon)
		self.setStyleSheet(GlobalTools.styleSheet)
		self.setFixedSize(310,190)
		self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
		
		aboutme=u'''
		Thank you for using LR2 Rival Ranking!<br>
		Current version: <font style="color:Gainsboro">%s</font><br>
		<br>
		Author: <font style="color:Gainsboro">Leo Shen</font><br>
		LR2IR: <font style="color:Gainsboro">うまい焼鴨 (<a href="http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=mypage&playerid=121168" style="color:Khaki">121168</a>)</font><br>
		Homepage: <a href="https://github.com/leoshen999/LR2RivalRanking" style="color:Khaki">GitHub</a><br>
		<br>
		Please contact us if having any question.'''%(GlobalTools.misc['version'])
		
		
		self.label=QtGui.QLabel(aboutme,self)
		self.label.setOpenExternalLinks(True)
		self.label.setGeometry(10,10,290,170)
	def closeEvent(self, event):
		self.hide()
		event.ignore()
	def showWindow(self):
		self.show()
		self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
		self.activateWindow()

class ModifyIrWindow(QtGui.QDialog):
	def __init__(self,parent=None):
		QtGui.QDialog.__init__(self,parent)
		self.setWindowTitle('Modify Ir/ data in LR2')
		self.setWindowIcon(GlobalTools.windowIcon)
		self.setStyleSheet(GlobalTools.styleSheet)
		self.setFixedSize(310,140)
		self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
		
		
		path=GlobalTools.misc['lr2exepath']
		self.labelPath=QtGui.QLabel('LR2.exe location:',self)
		self.labelPath.setGeometry(10,10,120,20)
		self.lineEditPath=QtGui.QLineEdit(path,self)
		self.lineEditPath.setGeometry(30,30,200,20)
		self.lineEditPath.setStyleSheet('border: 1px solid rgb(150,150,150);color: Gainsboro;')
		self.buttonBrowse=HoverButton('Browse',self)
		self.buttonBrowse.setGeometry(240,30,60,20)
		self.buttonBrowse.setStyleSheet('border: 1px solid rgb(150,150,150);')
		self.buttonBrowse.clicked.connect(self.selectFile)
		
		self.labelLastupdate=QtGui.QLabel('Last update:',self)
		self.labelLastupdate.setGeometry(10,60,120,20)
		self.labelTime=QtGui.QLabel(GlobalTools.misc['irlastupdate'],self)
		self.labelTime.setStyleSheet('color: Gainsboro;')
		self.labelTime.setGeometry(30,80,270,20)
		
		
		GlobalTools.logger.signalWriteIrLastupdate.connect(self.writeIrLastupdate)
		
		self.buttonOK=HoverButton('OK',self)
		self.buttonOK.setGeometry(170,110,60,20)
		self.buttonOK.clicked.connect(self.startModifyIr)
		self.buttonOK.clicked.connect(self.close)
		
		self.buttonCancel=HoverButton('Cancel',self)
		self.buttonCancel.setGeometry(240,110,60,20)
		self.buttonCancel.clicked.connect(self.close)
		
	def selectFile(self):
		path=QtGui.QFileDialog.getOpenFileName(
			self,caption='Specify the location of LR2.exe',
			filter='Executable (*.exe)',
			directory=self.lineEditPath.text())
		if path:
			self.lineEditPath.setText(path)
	def startModifyIr(self):
		path=unicode(self.lineEditPath.text().toUtf8(), encoding="utf_8")
		thr=threading.Thread(target=ModifyIrHandler.modifyIr,args=(path,))
		thr.daemon=True
		thr.start()
		GlobalTools.mainWindow.showWindow()
	def writeIrLastupdate(self,string):
		self.labelTime.setText(string)
	def closeEvent(self, event):
		self.hide()
		event.ignore()
	def showWindow(self):
		self.show()
		self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
		self.activateWindow()

class UpdateDifficultiesWindow(QtGui.QDialog):
	def __init__(self,parent=None):
		QtGui.QDialog.__init__(self,parent)
		self.setWindowTitle('Update difficulty tables')
		self.setWindowIcon(GlobalTools.windowIcon)
		self.setStyleSheet(GlobalTools.styleSheet)
		self.setFixedSize(310,90)
		self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
		
		
		self.labelLastupdate=QtGui.QLabel('Last update:',self)
		self.labelLastupdate.setGeometry(10,10,120,20)
		self.labelTime=QtGui.QLabel(GlobalTools.misc['difficultieslastupdate'],self)
		self.labelTime.setStyleSheet('color: Gainsboro;')
		self.labelTime.setGeometry(30,30,270,20)
		
		
		GlobalTools.logger.signalWriteDifficultiesLastupdate.connect(self.writeDifficultiesLastupdate)
		
		self.buttonOK=HoverButton('OK',self)
		self.buttonOK.setGeometry(170,60,60,20)
		self.buttonOK.clicked.connect(self.startUpdateDifficulties)
		self.buttonOK.clicked.connect(self.close)
		
		self.buttonCancel=HoverButton('Cancel',self)
		self.buttonCancel.setGeometry(240,60,60,20)
		self.buttonCancel.clicked.connect(self.close)
		
	def startUpdateDifficulties(self):
		thr=threading.Thread(target=UpdateDifficultiesHandler.updateDifficulties)
		thr.daemon=True
		thr.start()
		GlobalTools.mainWindow.showWindow()
	def writeDifficultiesLastupdate(self,string):
		self.labelTime.setText(string)
	def closeEvent(self, event):
		self.hide()
		event.ignore()
	def showWindow(self):
		self.show()
		self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
		self.activateWindow()