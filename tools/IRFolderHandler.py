#coding: utf-8
import Database
import GlobalTools
import WebpageParser
import sqlite3
import os

import RivalUpdater
import RankingGenerator

def modifyIRFolder(id,path):
	with Database.lock:
		GlobalTools.logger.write( '----- Modify Ir/ folder data -----\n' )
		hashs=[]
		conn=''
		cur=''
		
		# get all recorded song in LR2 song.db
		lr2dbpath=os.path.dirname(os.path.realpath(path))+'\\LR2files\\Database\\song.db'
		lr2irfolder=os.path.dirname(os.path.realpath(path))+'\\LR2files\\Ir\\'
		try:
			conn = sqlite3.connect(lr2dbpath)
			conn.row_factory = sqlite3.Row
			cur = conn.cursor()
			cur.execute('''
				SELECT hash
				FROM song
			''')
		except sqlite3.Error as er:
			if isinstance(conn,sqlite3.Connection):
				conn.close()
			GlobalTools.logger.write( '   Failed to read LR2 database    \n' )
			GlobalTools.logger.write( '----------------------------------\n' )
			GlobalTools.logger.write( '\n' )
			return
		hashs=cur.fetchall()
		conn.close()
		
		conn = sqlite3.connect(Database.path)
		conn.row_factory = sqlite3.Row
		cur = conn.cursor()
		
		# save lr2exe location
		try:
			cur.execute('''
				REPLACE INTO misc VALUES('lr2exepath',?)
			''',(path,))
			conn.commit()
		except sqlite3.Error as er:
			conn.rollback()
			conn.close()
			GlobalTools.logger.write( '  Failed to save LR2exe location  \n' )
			GlobalTools.logger.write( '----------------------------------\n' )
			GlobalTools.logger.write( '\n' )
			return
		
		# back up the original active list of rivals
		cur.execute('''
			SELECT id,active
			FROM rivals
			WHERE active>0
		''')
		temp=cur.fetchall()
		conn.close()
		pid_backup=''
		rids_backup=[]
		for rr in temp:
			if rr['active']==2:
				pid_backup=str(rr['id'])
			rids_backup.append(str(rr['id']))
		
		# get new rival lists
		pid=''
		if id=='backup':
			pid=pid_backup
		else:
			pid=id
		if not pid:
			GlobalTools.logger.write( '   Failed to get current player   \n' )
			GlobalTools.logger.write( '----------------------------------\n' )
			GlobalTools.logger.write( '\n' )
			return
		rids=WebpageParser.getRivals(pid)
		status=RivalUpdater.updateRival(pid,rids,True)
		if not status:
			GlobalTools.logger.write( '   Failed to update rival list    \n' )
			GlobalTools.logger.write( '----------------------------------\n' )
			GlobalTools.logger.write( '\n' )
			return
		
		# update all xml in Ir/ folder
		cnt=0
		hashs_l=len(hashs)
		GlobalTools.logger.write( ' Progress:                        \n' )
		for hh in hashs:
			hash=hh['hash']
			cnt+=1
			if cnt%100==1 or cnt==hashs_l:
				cntMessage='%d/%d'%(cnt,hashs_l)
				leftPad=' '*(24-len(cntMessage))
				cntMessage='<font\tstyle="color:LightGray">%d</font>/%d'%(cnt,hashs_l)
				GlobalTools.logger.writeCurrentLine( ' Progress:'+leftPad+cntMessage+'\n' )
			if not hash or not len(hash)==32 : continue
			body=RankingGenerator.generateRanking(hash,False)
			body+='\0'
			file=open(lr2irfolder+hash+'.xml','w')
			file.write(body)
			file.close()
		
		# recover original rival list
		conn = sqlite3.connect(Database.path)
		conn.row_factory = sqlite3.Row
		cur = conn.cursor()
		try:
			cur.execute('''
				UPDATE rivals SET active=0
			''')
			conn.commit()
		except sqlite3.Error as er:
			conn.rollback()
			conn.close()
			GlobalTools.logger.write( '   Failed to recover rival list   \n' )
			GlobalTools.logger.write( '----------------------------------\n' )
			GlobalTools.logger.write( '\n' )
			return
		for rid in rids_backup:
			active=1
			if rid==pid_backup:
				active=2
			try:
				cur.execute('''
					UPDATE rivals SET active=? WHERE id=?
				''',(active,rid))
				conn.commit()
			except sqlite3.Error as er:
				conn.rollback()
				conn.close()
				GlobalTools.logger.write( '   Failed to recover rival list   \n' )
				GlobalTools.logger.write( '----------------------------------\n' )
				GlobalTools.logger.write( '\n' )
				return
		conn.close()
		GlobalTools.logger.write( '----------------------------------\n' )
		GlobalTools.logger.write( '\n' )
