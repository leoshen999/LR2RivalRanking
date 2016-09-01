#coding: utf-8
import sqlite3
import threading
import sys
import os
lock = threading.Lock()

path=''

def init():
	global path
	
	dir_path = '%s\\LR2RR\\' %  os.environ['APPDATA'] 
	if not os.path.exists(dir_path):
		os.makedirs(dir_path)
	path = '%sdata.db' % dir_path
	with lock:
		conn = sqlite3.connect(path)
		conn.row_factory = sqlite3.Row
		cur = conn.cursor()
		try:
			cur.execute('''
				CREATE TABLE IF NOT EXISTS
				rivals(
					id INTEGER NOT NULL UNIQUE,
					name TEXT,
					lastupdate INTEGER NOT NULL,
					active INTEGER
				)''')
			cur.execute('''
				CREATE TABLE IF NOT EXISTS
				scores(
					hash TEXT NOT NULL,
					id INTEGER NOT NULL,
					clear INTEGER NOT NULL,
					notes INTEGER NOT NULL,
					combo INTEGER NOT NULL,
					pg INTEGER NOT NULL,
					gr INTEGER NOT NULL,
					minbp INTEGER NOT NULL,
					UNIQUE(hash, id)
				)''')
			conn.commit()
		except:
			conn.rollback()
			sys.exit()
		conn.close()