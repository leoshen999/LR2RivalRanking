#coding: utf-8

from PyQt4 import QtGui, QtCore
from StringIO import StringIO
import sys
import os
import win32api
import threading
import sqlite3

import GlobalTools
import Database
import IRFolderHandler


class HoverButton(QtGui.QPushButton):
	def __init__(self, text='', parent=None):
		QtGui.QPushButton.__init__(self, text, parent)
		self.setMouseTracking(True)

	def enterEvent(self, event):
		self.setStyleSheet('border: 1px solid LightGray;color: LightGray;')

	def leaveEvent(self, event):
		self.setStyleSheet('border: 1px solid rgb(150,150,150);')


class AboutWindow(QtGui.QDialog):
	def __init__(self,parent,version):
		QtGui.QDialog.__init__(self,parent)
		
		str=''
		str+='Thank you for using LR2 Rival Ranking!<br>'
		str+='Current version: <font style="color:LightGray">'+version+'</font><br>'
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
		self.setFixedSize(310,260)
		self.setWindowTitle('Modify Ir/ data in LR2')
		self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
		
		self.labelID=QtGui.QLabel('LR2ID:',self)
		self.labelID.setGeometry(10,10,50,25)
		
		self.radioButton1=QtGui.QRadioButton('Use current player in database',self)
		self.radioButton1.setGeometry(30,35,270,25)
		self.radioButton1.setChecked(True)
		
		self.radioButton2=QtGui.QRadioButton('Enter an ID:',self)
		self.radioButton2.setGeometry(30,60,110,25)
		self.lineEditID=QtGui.QLineEdit('',self)
		self.lineEditID.setGeometry(140,61,70,23)
		self.lineEditID.setStyleSheet('border: 1px solid rgb(150,150,150);')
		self.lineEditID.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[0-9]{1,6}")))
		
		conn = sqlite3.connect(Database.path)
		conn.row_factory = sqlite3.Row
		cur = conn.cursor()
		cur.execute('''
			SELECT value FROM misc WHERE key='lr2exepath'
		''')
		path=cur.fetchall()[0]['value']
		conn.close()
		self.labelPath=QtGui.QLabel('LR2.exe location:',self)
		self.labelPath.setGeometry(10,90,120,25)
		self.lineEditPath=QtGui.QLineEdit(path,self)
		self.lineEditPath.setGeometry(30,116,200,23)
		self.lineEditPath.setStyleSheet('border: 1px solid rgb(150,150,150);')
		self.buttonBrowse=HoverButton('Browse',self)
		self.buttonBrowse.setGeometry(235,116,60,23)
		self.buttonBrowse.setStyleSheet('border: 1px solid rgb(150,150,150);')
		self.buttonBrowse.clicked.connect(self.selectFile)
		
		str ='<font style="color:Salmon"># Caution: This function may cost much<br>'
		str+='&nbsp;&nbsp;time and create lots of xml files in<br>'
		str+='&nbsp;&nbsp;the Ir/ folder.</font>'
		self.labelCaution=QtGui.QLabel(str,self)
		self.labelCaution.setGeometry(10,145,290,75)
		
		self.buttonOK=HoverButton('OK',self)
		self.buttonOK.setGeometry(160,221,60,23)
		self.buttonOK.setStyleSheet('border: 1px solid rgb(150,150,150);')
		self.buttonOK.clicked.connect(self.startModifyIRFolder)
		self.buttonOK.clicked.connect(self.close)
		
		self.buttonCancel=HoverButton('Cancel',self)
		self.buttonCancel.setGeometry(235,221,60,23)
		self.buttonCancel.setStyleSheet('border: 1px solid rgb(150,150,150);')
		self.buttonCancel.clicked.connect(self.close)
		
	def selectFile(self):
		path=QtGui.QFileDialog.getOpenFileName(self,caption='Specify the location of LR2.exe',filter='Executable (*.exe)')
		if path:
			self.lineEditPath.setText(path)
	def startModifyIRFolder(self):
		id='backup'
		if self.radioButton2.isChecked():
			id=str(self.lineEditID.text())
		path=unicode(self.lineEditPath.text().toUtf8(), encoding="utf_8")
		thr=threading.Thread(target=IRFolderHandler.modifyIRFolder,args=(id,path))
		thr.daemon=True
		thr.start()
class MainWindow(QtGui.QTextBrowser):
	def __init__(self,original_hosts,version):
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
		
		self.aboutWindow=AboutWindow(self,version)
		self.modifyIRWindow=ModifyIRWindow(self)
		
		GlobalTools.printHelloMessage()
		
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
			self.aboutWindow.show()
		elif event.key()==QtCore.Qt.Key_F2:
			self.modifyIRWindow.show()
		elif event.key()==QtCore.Qt.Key_F3:
			thr=threading.Thread(target=GlobalTools.printDatabaseStatus)
			thr.daemon=True
			thr.start()
		elif event.key()==QtCore.Qt.Key_F4:
			thr=threading.Thread(target=GlobalTools.printHelloMessage)
			thr.daemon=True
			thr.start()

