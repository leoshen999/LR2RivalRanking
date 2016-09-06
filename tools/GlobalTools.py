#coding: utf-8

import win32api
import StringIO
import unicodedata
from PyQt4 import QtCore

# Need to know the supported charaters for Consolas for text alignment
supportedUnicode=[]
for str in win32api.LoadResource(0, u'SUPPORTEDUNICODE_TXT', 3).split('\n') :
	supportedUnicode.append(int(str,16))

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

# global logger: redirect message to QT
class Logger(QtCore.QObject):
	signal = QtCore.pyqtSignal(object)
	def write(self,string):
		self.signal.emit(string)
	def flush(self):
		pass
logger=Logger()
