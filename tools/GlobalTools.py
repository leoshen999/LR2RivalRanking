#coding: utf-8

import unicodedata
from PyQt4 import QtCore

def strWidth(str):
	width=0
	for ch in unicode(str):
		status = unicodedata.east_asian_width(ch)
		if status=='W' or status=='F' : width+=2
		else: width+=1
	return width

def strTruncateTo34(str):
	width=0
	result=''
	for ch in unicode(str):
		status = unicodedata.east_asian_width(ch)
		if status=='W' or status=='F' : width+=2
		else: width+=1
		result+=ch
		if width==32:
			result+='..'
			break
		if width==33:
			result+='.'
			break
	return result

class Logger(QtCore.QObject):
	signal = QtCore.pyqtSignal(object)
	def write(self,string):
		self.signal.emit(string)
	def flush(self):
		pass
logger=Logger()
