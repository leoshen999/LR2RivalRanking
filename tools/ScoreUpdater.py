#coding: utf-8
import time
import sqlite3
import GlobalTools
import WebpageParser

def updateScore(score):
	title,artist=WebpageParser.getTitleAndArtist(score['hash'])
	current_time=int(time.time())
	with GlobalTools.dbLock:
		try:
			GlobalTools.cur.execute('''
				REPLACE INTO scores VALUES(?,?,?,?,?,?,?,?)
			''',(score['hash'],score['id'],score['clear'],score['notes'],score['combo'],score['pg'],score['gr'],score['minbp']))
			GlobalTools.cur.execute('''
				REPLACE INTO recent VALUES(?,?,?,?)
			''',(score['hash'],score['id'],title,current_time))
			GlobalTools.cur.execute('''
				DELETE FROM recent
				WHERE id=? AND hash NOT IN(
					SELECT hash FROM recent WHERE id=? ORDER BY lastupdate DESC LIMIT 30
				)
			''',(score['id'],score['id']))
			GlobalTools.conn.commit()
		except Exception as e:
			GlobalTools.conn.rollback()