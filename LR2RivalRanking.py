#coding: utf-8

from PyQt4 import QtGui
import sys
import threading
import os

from tools import Gui
from tools import Server
from tools import Database

from tools import GlobalTools

version='v1.2.2'

if __name__ == '__main__':
	
	# init database
	Database.init()
	
	# modify hosts to redirect http request
	original_hosts=''
	file=open( os.environ['SystemRoot']+'\\System32\\drivers\\etc\\hosts','r')
	lines=file.read().split('\n')
	eol=''
	for line in lines:
		if line=='127.0.0.1 www.dream-pro.info':
			continue
		original_hosts+=(eol+line)
		eol='\n'
	file.close()
	file=open( os.environ['SystemRoot']+'\\System32\\drivers\\etc\\hosts','w')
	file.write(original_hosts+'\n127.0.0.1 www.dream-pro.info')
	file.close()
	
	# build up Qt GUI display
	app = QtGui.QApplication(sys.argv)
	mainWindow = Gui.MainWindow(original_hosts,version)
	mainWindow.show()
	
	# start another thread for HTTPServer
	thr=threading.Thread(target=Server.startServer)
	thr.daemon=True
	thr.start()
	
	# say sth when the app starts
	GlobalTools.printHelloMessage()
	
	sys.exit(app.exec_())
