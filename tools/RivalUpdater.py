#coding: utf-8
import time
import lxml.etree
import DPISocket
import GlobalTools
import WebpageParser

extra_parser = lxml.etree.XMLParser(encoding='cp932')
def updateRival(pid):
	rids = WebpageParser.getRivals(pid)
	with GlobalTools.logLock:
		try:
			with GlobalTools.dbLock:
				GlobalTools.cur.execute('UPDATE rivals SET active=0')
				GlobalTools.conn.commit()
			
			current_time=int(time.time())
			cnt=0
			len_rids=len(rids)
			for rid in rids:
				cnt=cnt+1
				with GlobalTools.dbLock:
					GlobalTools.cur.execute('SELECT lastupdate FROM rivals WHERE id=?',(rid,))
					lastupdate=GlobalTools.cur.fetchall()
				if len(lastupdate)<1: lastupdate=0
				else: lastupdate=lastupdate[0]['lastupdate']
				
				sock=DPISocket.DPISocket('GET','/~lavalse/LR2IR/2/getplayerxml.cgi?id=%s&lastupdate=%d' % (rid,lastupdate))
				res,body=sock.sendAndReceive()
				
				body=body[1:]
				doctype_end = body.find('>')+1
				body = body[:doctype_end] + '<dummyroot>' + body[doctype_end:] + '</dummyroot>'
				et=lxml.etree.fromstring(body, parser=extra_parser)
				score_tree=et.xpath('/dummyroot/scorelist/score')
				scores=[{ t.tag : t.text for t in score} for score in score_tree]
				name_tree=et.xpath('/dummyroot/rivalname')
				name=name_tree[0].text
				
				update_num='<span class="up-num">'+str(cnt)+'/'+str(len_rids)+'</span>'
				temp=''
				if pid==rid: temp=' pid'
				update_id='<span class="up-id'+temp+'"><a target="_blank" href="http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=mypage&amp;playerid='+rid+'">'+rid+'</a></span>'
				update_name='<span class="up-name'+temp+'"><a target="_blank" href="http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=mypage&amp;playerid='+rid+'">'+GlobalTools.convertHTMLEntities(name)+'</a></span>'
				temp=len(scores)
				if temp>0: temp='+'+str(temp)
				else: temp=''
				update_new='<span class="up-new">'+temp+'</span>'
				GlobalTools.logger.write('<div class="one-row">'+update_num+update_id+update_name+update_new+'</div>')
				
				
				active=1
				if rid==pid: active=2
				with GlobalTools.dbLock:
					for score in scores:
						if 'hash' not in score or not score['hash'] or not len(score['hash'])==32 : continue
						GlobalTools.cur.execute(
							'REPLACE INTO scores VALUES(?,?,?,?,?,?,?,?)',
							(score['hash'],rid,score['clear'],score['notes'],
							score['combo'],score['pg'],score['gr'],score['minbp'])
						)
					GlobalTools.cur.execute( 'REPLACE INTO rivals VALUES(?,?,?,?)',(rid,name,current_time,active) )
					GlobalTools.conn.commit()
		except Exception as e:
			GlobalTools.conn.rollback()
			GlobalTools.logger.write('<div class="one-row"><span class="title">Failed to setup database.</span></div>')
		GlobalTools.logger.write('<div class="one-row"><hr></div>')