#coding: utf-8
from urlparse import urlparse, parse_qs
import time
import lxml.html
import lxml.etree
import sqlite3

import Database
import DPISocket
import GlobalTools

extra_parser = lxml.etree.XMLParser(encoding='shift_jis')

def updateRivalList(q_dict):
	with Database.lock:
		GlobalTools.logger.write( '------- Update rival list --------\n' )
		pid=''
		rids=[]
		
		# parse the rival id list from the personal page of current player
		# if id not exists, the rival list should be empty
		if('id' in q_dict):
			pid = q_dict['id'][0]
			rids.append(pid)
			sock = DPISocket.DPISocket('GET','/~lavalse/LR2IR/search.cgi?mode=mypage&playerid=%s' % (pid) )
			res, body = sock.sendAndReceive()
			root=lxml.html.fromstring(body)
			table=root.find('.//table')
			if table is not None :
				for tr in table.findall('.//tr'):
					if tr.find('th').text==u'ライバル':
						for a in tr.find('td').findall('a'):
							rids.append( parse_qs(urlparse(a.attrib['href']).query)['playerid'][0] )
		
		conn = sqlite3.connect(Database.path)
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
			GlobalTools.logger.write( '    Failed to reset rival list    \n' )
			GlobalTools.logger.write( '----------------------------------\n' )
			GlobalTools.logger.write( '\n' )
			return
		
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
			
			# write the rival information to log
			cnt_message=''
			if(len(rids)<10):
				cnt_message=' %d/%d' %(cnt,len(rids))
			elif(len(rids)<100):
				cnt_message=' %2d/%2d' %(cnt,len(rids))
			elif(len(rids)<1000):
				cnt_message=' %3d/%3d' %(cnt,len(rids))
			else:
				cnt_message=' %4d/%4d' %(cnt,len(rids))
			active=1
			id_message=''
			if rid == pid:
				id_message= ' <font\tstyle="color:Khaki">%06d %s</font>' % (int(rid),name)
				active=2
			else: 
				id_message= ' <font\tstyle="color:LightGray">%06d %s</font>' % (int(rid),name)
			update_message=''
			leftPad=''
			if not len(scores)==0:
				update_message='<font\tstyle="color:DodgerBlue">+%d</font>' %(len(scores))
				width=len(cnt_message)+8+GlobalTools.strWidth(name)
				width2=len( '+%d'%(len(scores)) )
				if width+width2<34:
					leftPad=' '*(34-width-width2)
			else:
				width=len(cnt_message)+8+GlobalTools.strWidth(name)
				if width<34:
					leftPad=' '*(34-width)
			GlobalTools.logger.write( cnt_message+id_message+leftPad+update_message+'\n' )
			
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
				GlobalTools.logger.write( '   Failed to update rival score   \n' )
				GlobalTools.logger.write( '----------------------------------\n' )
				GlobalTools.logger.write( '\n' )
				return
		conn.close()
		GlobalTools.logger.write( '----------------------------------\n' )
		GlobalTools.logger.write( '\n' )