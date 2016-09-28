#coding: utf-8
from urlparse import urlparse, parse_qs
import lxml.html
import lxml.etree
import sqlite3
import Database
from PyQt4 import QtCore

class DifficultyPageGenerator(QtCore.QObject):
	signalDone=QtCore.pyqtSignal(object)
	def generateDifficultyPage(self,table):
		print 'generateDifficultPage', table
		str='''<html>
			<head>
				<style>
					*{
						font-size: 10pt;
						font-family: ConsolasHigh,"MS Gothic";
					}
					html, body{
						background-color:rgb(20,20,20);
						color: rgb(230,230,230);
					}
				</style>
			</head>
			<body>
				YAYA<br/>YAYA<br/>YAYA<br/>YAYA<br/>YAYA<br/>YAYA<br/>YAYA<br/>YAYA<br/>YAYA<br/>YAYA<br/>YAYA<br/>YAYA<br/>YAYA<br/>
			</body>
		</html>'''
		self.signalDone.emit(str)