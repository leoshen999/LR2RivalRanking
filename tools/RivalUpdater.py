#coding: utf-8
import time
import lxml.html
import lxml.etree
import sqlite3

import DPISocket
import GlobalTools

extra_parser = lxml.etree.XMLParser(encoding='cp932')

def updateRival(pid,rids,toPrint=True):
	conn = sqlite3.connect(GlobalTools.dbpath)
	conn.row_factory = sqlite3.Row
	cur = conn.cursor()
	# reset all players in database to inactive
	try:
		cur.execute('''
			UPDATE rivals SET active=0
		''')
		conn.commit()
	except sqlite3.Error as er:
		conn.rollback()
		conn.close()
		return False
	
	current_time=int(time.time())
	cnt=0
	for rid in rids:
		cnt=cnt+1
		
		# get the player scores from getplayerxml.cgi and update database
		cur.execute('''
			SELECT lastupdate FROM rivals WHERE id=?
		''',(rid,))
		lastupdate=cur.fetchall()
		if not lastupdate:
			lastupdate=0
		else:
			lastupdate=lastupdate[0]['lastupdate']
		
		sock=DPISocket.DPISocket('GET','/~lavalse/LR2IR/2/getplayerxml.cgi?id=%s&lastupdate=%d' % (rid,lastupdate))
		res,body=sock.sendAndReceive()
		
		# create the correct format of xml for parsing (the original one is not really an xml)
		body=body[1:]
		doctype_end = body.find('>')+1
		body = body[:doctype_end] + '<dummyroot>' + body[doctype_end:] + '</dummyroot>'
		et=lxml.etree.fromstring(body, parser=extra_parser)
		score_tree=et.xpath('/dummyroot/scorelist/score')
		scores=[{ t.tag : t.text for t in score} for score in score_tree]
		name_tree=et.xpath('/dummyroot/rivalname')
		name=name_tree[0].text
		
		active=1
		if rid==pid:
			active=2
		
		# write the rival information to log
		if toPrint:
			cntMessage=''
			idMessage=''
			updateMessage=''
			leftPad=''
			
			if(len(rids)<10):
				cntMessage=' %d/%d' %(cnt,len(rids))
			elif(len(rids)<100):
				cntMessage=' %2d/%2d' %(cnt,len(rids))
			elif(len(rids)<1000):
				cntMessage=' %3d/%3d' %(cnt,len(rids))
			else:
				cntMessage=' %4d/%4d' %(cnt,len(rids))
			
			url='http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=mypage&playerid='+rid
			name2=GlobalTools.convertHTMLEntities(name)
			if active==2:
				idMessage= ' <a\thref="'+url+'"\tstyle="color:Khaki;text-decoration:none">%06d %s</a>' % (int(rid),name2)
			else: 
				idMessage= ' <a\thref="'+url+'"\tstyle="color:LightGray;text-decoration:none">%06d %s</a>' % (int(rid),name2)
			
			if not len(scores)==0:
				updateMessage='<font\tstyle="color:DodgerBlue">+%d</font>' %(len(scores))
				width=len(cntMessage)+8+GlobalTools.strWidth(name)
				width2=len( '+%d'%(len(scores)) )
				if width+width2<34:
					leftPad=' '*(34-width-width2)
			else:
				width=len(cntMessage)+8+GlobalTools.strWidth(name)
				if width<34:
					leftPad=' '*(34-width)
			GlobalTools.logger.write( cntMessage+idMessage+leftPad+updateMessage+'\n' )
		
		# update database for all scores
		try:
			for score in scores:
				if 'hash' not in score or not score['hash'] or not len(score['hash'])==32 : continue
				cur.execute('''
					REPLACE INTO scores VALUES(?,?,?,?,?,?,?,?)
				''',(score['hash'],rid,score['clear'],score['notes'],score['combo'],score['pg'],score['gr'],score['minbp']))
			cur.execute('''
				REPLACE INTO rivals VALUES(?,?,?,?)
			''',(rid,name,current_time,active))
			conn.commit()
		except sqlite3.Error as er:
			conn.rollback()
			conn.close()
			return False
	conn.close()
	return True