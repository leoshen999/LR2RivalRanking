#coding: utf-8
import datetime,time
import os
import sqlite3

import GlobalTools
import RankingGenerator

def modifyIr(path):
	with GlobalTools.logLock:
		try:
			conn=''
			cur=''
			
			lr2dbpath=os.path.dirname(os.path.realpath(path))+'\\LR2files\\Database\\song.db'
			lr2irfolder=os.path.dirname(os.path.realpath(path))+'\\LR2files\\Ir\\'
			
			conn = sqlite3.connect(lr2dbpath)
			conn.row_factory = sqlite3.Row
			cur = conn.cursor()
			cur.execute('SELECT hash FROM song')
			hashs=cur.fetchall()
			conn.close()
			
			cnt=0
			hashs_l=len(hashs)
			
			GlobalTools.logger.write( '<div class="one-row"><span class="title">Modify Ir/ progress: <span class="highlight">0 / '+str(hashs_l)+'</span></span></div>' )
			for hh in hashs:
				hash=hh['hash']
				cnt+=1
				if cnt%100==1 or cnt==hashs_l:
					GlobalTools.logger.write( '<div class="one-row"><span class="title">Modify Ir/ progress: <span class="highlight">'+str(cnt)+' / '+str(hashs_l)+'</span></span></div>',False )
				if not hash or not len(hash)==32 : continue
				body=RankingGenerator.generateRankingXML(hash,False)
				body+='\0'
				with open(lr2irfolder+hash+'.xml','w') as file:
					file.write(body)
			with GlobalTools.dbLock:
				GlobalTools.misc['lr2exepath']=path
				GlobalTools.cur.execute('REPLACE INTO misc VALUES("lr2exepath",?)',(GlobalTools.misc['lr2exepath'],))
				
				GlobalTools.misc['irlastupdate']=datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')
				GlobalTools.cur.execute('REPLACE INTO misc VALUES("irlastupdate",?)',(GlobalTools.misc['irlastupdate'],))
				GlobalTools.logger.writeIrLastupdate(GlobalTools.misc['irlastupdate'])
				GlobalTools.conn.commit()
		except Exception as e:
			if isinstance(conn,sqlite3.Connection): conn.close()
			GlobalTools.conn.rollback()
			GlobalTools.logger.write('<div class="one-row"><span class="title">Failed to modify Ir/.</span></div>')
		GlobalTools.logger.write('<div class="one-row"><hr></div>')