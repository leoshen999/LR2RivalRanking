#coding: utf-8
from PyQt4 import QtGui, QtCore, QtWebKit
from StringIO import StringIO
import os
import sys
import webbrowser

import SubWindow
import GlobalTools

class WebView(QtWebKit.QWebView):
	def __init__(self,parent=None):
		QtWebKit.QWebView.__init__(self,parent)
		self.setHtml('''<!DOCTYPE html>
		<html>
		<head>
		<meta charset="utf-8">
		<style>
			body{
				font-size: 10pt;
				font-family: ConsolasHigh,Meiryo;
				color:DarkGray;
				background-color: black;
				text-align: center;
				overflow-y: scroll;
				margin: 0px;
				-webkit-user-select: none;
			}
			::-webkit-scrollbar {width: 10px;}
			::-webkit-scrollbar-track {background-color: Black;}
			::-webkit-scrollbar-thumb {background-color: rgb(64,64,64);}
			::-webkit-scrollbar-button {display:none;}
			a{color:Gainsboro;text-decoration:none;}
			.one-row{
				line-height: 20px;
				margin-top: 1px;
				margin-bottom: 1px;
			}
			.one-row span{
				height: 20px;
				display: inline-block;
				overflow:hidden;
				white-space: nowrap;
				text-overflow: ellipsis;
				vertical-align: top;
			}
			.title{width: 260px;}
			.highlight{color:Gainsboro;}
			.pid a{color:Khaki !important;}
			
			.up-num{width: 50px;text-align:right;}
			.up-id{width: 50px;text-align:right;}
			.up-name{width: 100px;text-align:left;padding-left:10px;}
			.up-new{width: 46px;color: rgb(160,160,255);text-align:right;padding-right:4px;}
			
			.rank-num{width: 35px;}
			.rank-num.TOP1{color: Gold !important;text-shadow: -2px 0px 8px Gold,2px 0px 8px Gold;}
			.rank-name{width: 85px;}
			.rank-clear{width: 25px;}
			.rank-clear.FC{
				color: hsl(330, 100%, 80%);
				text-shadow: -2px 0px 8px hsl(330, 100%, 80%),2px 0px 8px hsl(330, 100%, 80%);
			}
			.rank-clear.HC{
				color: hsl(260, 20%, 85%);
				text-shadow: -2px 0px 8px hsl(260, 20%, 85%),2px 0px 8px hsl(260, 20%, 85%);
			}
			.rank-clear.CL{color: hsl(35, 75%, 60%);}
			.rank-clear.EC{color: hsl(90, 55%, 45%);}
			.rank-clear.FA{color: hsl(0, 100%, 20%);}
			.rank-score{
				width: 115px;
				text-align: left;
				text-shadow: -2px 0px 8px rgba(0,0,0,0.85),2px 0px 8px rgba(0,0,0,0.85);
				color:Gainsboro;
			}
			.rank-score .MAX{background: hsl(20, 80%, 60%);}
			.rank-score .AAA{background: hsl(45, 70%, 55%);}
			.rank-score .AA{background: hsl(180, 30%, 60%);}
			.rank-score .A{background: hsl(210, 40%, 50%);}
			.rank-score .BF{background: hsl(270, 5%, 40%);}
		</style>
		<script src="https://code.jquery.com/jquery-3.1.1.min.js"></script>
		<script>
			function writeLog(string,newLine){
				if(!newLine)
					$("body").find('.one-row:last').remove();
				$("body").append(string);
				$("body").find('.one-row:lt(-150)').remove();
				window.scrollTo(0,document.body.scrollHeight);
			}
		</script>
		</head>
		<body>
		</body>
		</html>
		''')
		self.page().setLinkDelegationPolicy(2)
		self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
		
		GlobalTools.logger.signalWrite.connect(self.writeLog)
		self.linkClicked.connect(self.openLink)
	def writeLog(self,string,newLine):
		if newLine: nl='true'
		else: nl='false'
		self.page().mainFrame().evaluateJavaScript('writeLog(\''+string+'\','+nl+')')
	def openLink(self,url):
		webbrowser.open(url.toString())

class SystemTrayIcon(QtGui.QSystemTrayIcon):
	def __init__(self, parent=None):
		QtGui.QSystemTrayIcon.__init__(self, parent)
		self.setIcon(GlobalTools.windowIcon)
		
		self.menu=QtGui.QMenu()
		self.menu.LR2RRAction = self.menu.addAction("LR2RR")
		self.menu.LR2IRAction = self.menu.addAction("LR2IR")
		self.menu.addSeparator()
		self.menu.exitAction = self.menu.addAction("Exit")
		
		self.setContextMenu(self.menu)

class MenuBar(QtGui.QMenuBar):
	def __init__(self,parent=None):
		QtGui.QMenuBar.__init__(self,parent)
		
		self.setStyleSheet('''
			QMenuBar {background-color: rgb(32,32,32);}
			QMenuBar::item {
				spacing: 3px;
				padding: 1px 6px;
				background: transparent;
			}
			QMenuBar::item:selected{background: rgb(64,64,64);}
			QMenuBar::item:pressed {background: rgb(64,64,64);}
			
			QMenu {
				background-color: rgb(32,32,32);
				border: 1px solid rgb(64,64,64);
			}
			QMenu::item {
				padding: 0px;
				padding: 3px 8px;
			}
			QMenu::item:selected {background-color: rgb(64,64,64);}
			QMenu::separator {
				height: 1px;
				background: rgb(64,64,64);
			}
		''')
		
		
		self.mainmenu=self.addMenu("Main")
		self.mainmenu.modifyIrAction = self.mainmenu.addAction("Modify Ir/")
		self.mainmenu.modifyIrAction.setShortcut(QtGui.QKeySequence('Ctrl+1'))
		self.mainmenu.updateDifficultiesAction = self.mainmenu.addAction("Update difficulties")
		self.mainmenu.updateDifficultiesAction.setShortcut(QtGui.QKeySequence('Ctrl+2'))
		self.mainmenu.addSeparator()
		self.mainmenu.LR2IRAction = self.mainmenu.addAction("Visit LR2IR")
		self.mainmenu.LR2IRAction.setShortcut(QtGui.QKeySequence('Ctrl+3'))
		self.mainmenu.addSeparator()
		self.mainmenu.exitAction = self.mainmenu.addAction("Exit")
		
		# self.viewmenu=self.addMenu("View")
		
		self.questionmenu=self.addMenu('?')
		self.questionmenu.aboutAction = self.questionmenu.addAction("About LR2RR")
		self.questionmenu.aboutAction.setShortcut(QtGui.QKeySequence('F1'))

class MainWindow(QtGui.QMainWindow):
	def __init__(self,original_hosts):
		QtGui.QMainWindow.__init__(self,parent=None)
		self.original_hosts=original_hosts
		
		self.setWindowTitle('LR2 Rival Ranking')
		self.setWindowIcon(GlobalTools.windowIcon)
		self.setStyleSheet(GlobalTools.styleSheet)
		self.resize(270,400)
		self.setFixedWidth(270)
		self.setMinimumHeight(400)
		self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
		
		self.aboutWindow=SubWindow.AboutWindow()
		self.modifyIrWindow=SubWindow.ModifyIrWindow()
		self.updateDifficultiesWindow=SubWindow.UpdateDifficultiesWindow()
		
		self.webview=WebView(self)
		self.setCentralWidget(self.webview)
		
		self.menubar=MenuBar(self)
		self.setMenuBar(self.menubar)
		self.menubar.mainmenu.LR2IRAction.triggered.connect(self.visitLR2IR)
		self.menubar.mainmenu.modifyIrAction.triggered.connect(self.modifyIrWindow.showWindow)
		self.menubar.mainmenu.updateDifficultiesAction.triggered.connect(self.updateDifficultiesWindow.showWindow)
		self.menubar.mainmenu.exitAction.triggered.connect(self.closeAll)
		self.menubar.questionmenu.aboutAction.triggered.connect(self.aboutWindow.showWindow)
		
		self.tray = SystemTrayIcon(self)
		self.tray.activated.connect(self.trayClicked)
		self.tray.menu.LR2RRAction.triggered.connect(self.showWindow)
		self.tray.menu.LR2IRAction.triggered.connect(self.visitLR2IR)
		self.tray.menu.exitAction.triggered.connect(self.closeAll)
		self.tray.show()
		self.tray.showMessage("LR2RR", "LR2RR is working and hidden in the taskbar.")
		
		self.show()
		
	def trayClicked(self,value):
		if value==self.tray.DoubleClick: self.showWindow()
	def visitLR2IR(self):
		webbrowser.open('http://www.dream-pro.info/~lavalse/LR2IR/search.cgi')
	def closeAll(self):
		try:
			with open( os.environ['SystemRoot']+'\\System32\\drivers\\etc\\hosts','w') as file:
				file.write(self.original_hosts)
		except: pass
		QtCore.QCoreApplication.exit()
	def closeEvent(self, event):
		self.hide()
		event.ignore()
	def showWindow(self):
		self.show()
		self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
		self.activateWindow()