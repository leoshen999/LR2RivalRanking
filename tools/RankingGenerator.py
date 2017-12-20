#coding: utf-8
import time
import GlobalTools
import WebpageParser

def generateRankingXML(hash,toPrint=False):
	with GlobalTools.dbLock:
		try:
			GlobalTools.cur.execute('''
				SELECT rr.name AS name, rr.id AS id, ss.clear AS clear, ss.notes AS notes, 
						ss.combo AS combo, ss.pg AS pg, ss.gr AS gr, ss.minbp AS minbp, rr.active AS active
				FROM rivals AS rr INNER JOIN scores AS ss ON rr.id=ss.id
				WHERE rr.active>0 AND ss.hash=?
			''',(hash,))
			played=GlobalTools.cur.fetchall()
			GlobalTools.cur.execute('''
				SELECT name, id, 0 AS clear, 0 AS notes, 
						0 AS combo, 0 AS pg, 0 AS gr, 0 AS minbp, active
				FROM rivals
				WHERE active>0 AND NOT id IN(
					SELECT id FROM scores WHERE hash=?
				)
			''',(hash,))
			notplayed=GlobalTools.cur.fetchall()
		except sqlite3.Error as er: return ''
	
	scores=sorted(played+notplayed, key=(lambda score: (score['pg']*2+score['gr'])), reverse=True)
	
	body='<?xml version="1.0" encoding="shift_jis"?>\n'
	body+='<ranking>\n'
	for score in scores:
		body+='\t<score>\n'
		body+='\t\t<name>%s</name>\n' % score['name']
		body+='\t\t<id>%d</id>\n' % score['id']
		body+='\t\t<clear>%d</clear>\n' % score['clear']
		body+='\t\t<notes>%d</notes>\n' % score['notes']
		body+='\t\t<combo>%d</combo>\n' % score['combo']
		body+='\t\t<pg>%d</pg>\n' % score['pg']
		body+='\t\t<gr>%d</gr>\n' % score['gr']
		body+='\t\t<minbp>%d</minbp>\n' % score['minbp']
		body+='\t</score>\n'
	body+='</ranking>\n'
	body+='<lastupdate>%s</lastupdate>' % time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(int(time.time())))
	body=body.encode('cp932')
	
	
	if toPrint:
		title,artist=WebpageParser.getTitleAndArtist(hash)
		with GlobalTools.logLock:
			if title:
				GlobalTools.logger.write('<div class="one-row"><span class="title"><a target="_blank" href="http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=ranking&amp;bmsmd5=%s">%s</a></span></div>'%(hash,GlobalTools.convertHTMLEntities(title)))
			if artist:
				GlobalTools.logger.write('<div class="one-row"><span class="title"><a target="_blank" href="http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=ranking&amp;bmsmd5=%s">%s</a></span></div>'%(hash,GlobalTools.convertHTMLEntities(artist)))
			cnt=0
			prev_ex=99999999
			prev_num=0
			for score in scores:
				cnt+=1
				
				temp=''
				if score['active'] == 2:
					temp=' pid'
				rank_name='<span class="rank-name%s"><a target="_blank" href="http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=mypage&amp;playerid=%s">%s</a></span>'%(temp,str(score['id']),GlobalTools.convertHTMLEntities(score['name']))
				
				
				ex=score['pg']*2+score['gr']
				if ex < prev_ex:
					prev_ex = ex
					prev_num = cnt
				if score['clear'] == 0:
					rank_num = '<span class="rank-num"></span>'
					rank_clear = '<span class="rank-clear"></span>'
					rank_score = '<span class="rank-score"></span>'
				else:
					temp=''
					if prev_num == 1: temp=' TOP1'
					rank_num = '<span class="rank-num%s">%s</span>'%(temp,str(prev_num))
					
					temp=''
					if score['clear'] == 1: temp=' FA'
					elif score['clear'] == 2: temp=' EC'
					elif score['clear'] == 3: temp=' CL'
					elif score['clear'] == 4: temp=' HC'
					elif score['clear'] == 5: temp=' FC'
					rank_clear = '<span class="rank-clear%s">%s</span>'%(temp,temp)
					
					total=score['notes']*2
					temp=''
					if ex*9>=total*9: temp='MAX'
					elif ex*9>=total*8: temp='AAA'
					elif ex*9>=total*7: temp='AA'
					elif ex*9>=total*6: temp='A'
					else: temp='BF'
					
					ex_rate='%.2f%%'%(float(ex)/float(total)*100.0)
					rank_score = '<span class="rank-score"><div class="%s" style="width:%s">&nbsp;%s&nbsp;(%s)</div></span>'%(temp,ex_rate,ex_rate,str(ex))
					
				GlobalTools.logger.write('<div class="one-row">'+rank_num+rank_name+rank_clear+rank_score+'</div>')
			GlobalTools.logger.write('<div class="one-row"><hr></div>')
	return body