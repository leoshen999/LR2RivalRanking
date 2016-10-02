#coding: utf-8
import GlobalTools
import sqlite3
import os

import RankingGenerator

def modifyIRFolder(path):
	with GlobalTools.lock:
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
			if isinstance(conn,sqlite3.Connection): conn.close()
			GlobalTools.logger.write( '   Failed to read LR2 database    \n' )
			GlobalTools.logger.write( '----------------------------------\n' )
			GlobalTools.logger.write( '\n' )
			return
		hashs=cur.fetchall()
		conn.close()
		
		GlobalTools.misc['lr2exepath']=path
		conn = sqlite3.connect(GlobalTools.dbpath)
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
		
		GlobalTools.logger.write( '----------------------------------\n' )
		GlobalTools.logger.write( '\n' )
