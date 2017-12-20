#coding: utf-8
from PyQt4 import QtGui,QtCore
import sys
import threading
import os

from tools import GlobalTools
from tools import MainWindow
from tools import Server

version='v2.1'
if __name__ == '__main__':
	sys.stderr=sys.stdout
	app=QtGui.QApplication(sys.argv)
	GlobalTools.init(version)
	
	# modify hosts to redirect http request
	original_hosts=''
	with open( os.environ['SystemRoot']+'\\System32\\drivers\\etc\\hosts','r') as file:
		lines=file.read().split('\n')
		eol=''
		for line in lines:
			if line=='127.0.0.1 www.dream-pro.info':
				continue
			original_hosts+=(eol+line)
			eol='\n'
	with open( os.environ['SystemRoot']+'\\System32\\drivers\\etc\\hosts','w') as file:
		file.write(original_hosts+'\n127.0.0.1 www.dream-pro.info')
	
	# start another thread for HTTPServer
	thr=threading.Thread(target=Server.startServer)
	thr.daemon=True
	thr.start()
	
	GlobalTools.mainWindow = MainWindow.MainWindow(original_hosts)
	app.exec_()
