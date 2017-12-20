#coding: utf-8
import json
import GlobalTools
import DPISocket
import WebpageExtensionHandler

def getPlayerScore(hash):
	with GlobalTools.dbLock:
		GlobalTools.cur.execute('''
			SELECT rr.name AS name, rr.id AS id, ss.clear AS clear, ss.notes AS notes, 
					ss.pg*2+ss.gr AS score, ss.minbp AS minbp, rr.active AS active
			FROM rivals AS rr INNER JOIN scores AS ss ON rr.id=ss.id
			WHERE rr.active>0 AND ss.hash=?
			ORDER BY score DESC
		''',(hash,))
		played=GlobalTools.cur.fetchall()
	
	rr={}
	rr['lamp']=''
	rr['lamp_class']=' NO'
	rr['bp']=''
	rr['bp_class']=''
	rr['score']=''
	rr['score_class']=''
	rr['score_rate']=''
	rr['ranking']=''
	rr['ranking_class']=''
	rr['playedN']='-'
	rr['playedN_class']=' N0'
	
	prev_score=99999999
	prev_ranking=0
	cnt=0
	for pl in played:
		cnt+=1
		if pl['score']<prev_score:
			prev_ranking=cnt
			prev_score=pl['score']
		if pl['active'] == 2:
			temp=pl['clear']
			rr['lamp']=str(temp)
			if temp == 1 : rr['lamp_class']=' FA'
			elif temp == 2 : rr['lamp_class']=' EC'
			elif temp == 3 : rr['lamp_class']=' CL'
			elif temp == 4 : rr['lamp_class']=' HC'
			elif temp == 5 : rr['lamp_class']=' FC'
			
			temp=pl['minbp']
			rr['bp']=str(temp)
			if temp==0 : rr['bp_class']=' bp0'
			
			temp=pl['score']
			total=pl['notes']*2
			rr['score']='&nbsp;('+str(temp)+')'
			rr['score_class']=' BF'
			if temp*9>=total*9 : rr['score_class']=' MAX'
			elif temp*9>=total*8 : rr['score_class']=' AAA'
			elif temp*9>=total*7 : rr['score_class']=' AA'
			elif temp*9>=total*6 : rr['score_class']=' A'
			rr['score_rate']='%.2f%%' % (float(temp)/float(total)*100.0)
			
			rr['ranking']=str(prev_ranking)
			if prev_ranking == 1: rr['ranking_class']=' TOP1'
			elif prev_ranking == 2: rr['ranking_class']=' TOP2'
			elif prev_ranking == 3: rr['ranking_class']=' TOP3'
			break
	temp=len(played)
	if temp>0:
		rr['playedN']=str(temp)
		rr['playedN_class']=''
	return rr

def generateFilter(level_order):
	temp=len(level_order)
	filter='<div class="ck">MinLV:<span style="position:relative;display:inline-block;width:45px;height:20px;">&nbsp;<select class="ck-select min-lv" onchange="resetFilterResult()">'
	for idx in range(temp):
		if idx==0: filter+='<option value="%s" selected>%s</option>'%(str(idx),level_order[idx])
		else: filter+='<option value="%s">%s</option>'%(str(idx),level_order[idx])
	filter+='</select></span> Filter:'
	
	for rank in [['MAX','MAX'],['AAA','AAA'],['AA','AA'],['A','A'],['BF','B-F']]:
		filter+='<label class="ck-button RANK %s"><input type="checkbox" value="%s" checked onchange="resetFilterResult()"><span>%s</span></label>'%(rank[0],rank[0],rank[1])
	filter+=' '
	
	for clear in [['FC','FULLCOMBO'],['HC','HARD'],['CL','NORMAL'],['EC','EASY'],['FA','FAILED'],['NO','NOPLAY']]:
		filter+='<label class="ck-button CLEAR %s"><input type="checkbox" value="%s" checked onchange="resetFilterResult()"><span>%s</span></label>'%(clear[0],clear[0],clear[1])
	
	filter+='<br>MaxLV:<span style="position:relative;display:inline-block;width:45px;height:20px;">&nbsp;<select class="ck-select max-lv" onchange="resetFilterResult()">'
	for idx in range(temp):
		if idx==temp-1: filter+='<option value="%s" selected>%s</option>'%(str(idx),level_order[idx])
		else: filter+='<option value="%s">%s</option>'%(str(idx),level_order[idx])
	filter+='</select></span> Status:'
	
	for rank in ['MAX','AAA','AA','A','BF']:
		filter+='<span class="ck-status RANK %s"></span>'%(rank)
	filter+=' '
	for clear in ['FC','HC','CL','EC','FA','NO']:
		filter+='<span class="ck-status CLEAR %s"></span>'%(clear)
	filter+='</div>'
	
	lvs='['
	for level in level_order: lvs+='"'+level+'",'
	lvs+=']'
	filter+='<script>var level_order=%s;</script>'%(lvs)
	return filter

def generateTable(level_order,songs):
	
	table='''
		<table id="playerTable"><thead><tr>
			<th class="level leftborder2">Level</th>
			<th class="title">Title</th>
			<th class="lamp leftborder">L</th>
			<th class="bp">BP</th>
			<th class="score">Score</th>
			<th class="ranking rightborder">Ranking</th>
			<th class="playedN rightborder2">Played</th>
		</tr></thead><tbody>
	'''
	trs=[]
	for hash,song in songs.iteritems():
		cs=getPlayerScore(hash)
		
		tr='<tr class="song-tr%s%s" hidden-level="%s">'%(cs['lamp_class'],cs['score_class'],str(level_order.index(song[0])))
		tr+='<td class="level leftborder">%s</td>'%(song[0])
		tr+='<td class="title"><a target="_blank" href="http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=ranking&amp;bmsmd5=%s">%s</a></td>'%(hash,GlobalTools.convertHTMLEntities(song[1]))
		tr+='<td class="lamp leftborder%s"><span style="display:none">%s</span></td>'%(cs['lamp_class'],cs['lamp'])
		tr+='<td class="bp%s%s">%s</td>'%(cs['bp_class'],cs['lamp_class'],cs['bp'])
		tr+='<td class="score%s"><div class="%s" style="width:%s">&nbsp;%s%s</div></td>'%(cs['lamp_class'],cs['score_class'],cs['score_rate'],cs['score_rate'],cs['score'])
		tr+='<td class="ranking rightborder%s%s">%s</td>'%(cs['ranking_class'],cs['lamp_class'],cs['ranking'])
		tr+='<td class="playedN rightborder%s" hash="%s">%s</td>'%(cs['playedN_class'],hash,cs['playedN'])
		tr+='</tr>'
		trs.append(tr)
	table+= ''.join(trs)+'</tbody></table>'
	return table

def handleDifficultyPage(headers,q_dict):
	sock=DPISocket.DPISocket('GET','/~lavalse/LR2IR/search.cgi?mode=detail')
	sock.setMsg(headers)
	res,body=sock.sendAndReceive()
	
	table='normal_no2'
	if 'table' in q_dict and q_dict['table'] in GlobalTools.table_info:
		table = q_dict['table']
	pre_def='''
		<script src="https://code.jquery.com/jquery-3.1.1.min.js"></script>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.27.8/js/jquery.tablesorter.min.js"></script>
		<style>%s</style>'''%(GlobalTools.webstyle)
	
	title='<div class="big-title">%s</div>'%(GlobalTools.table_info[table][0])
	loading='<div class="small-title" id="loading">Loading...</div>'
	post_def='<script>var mode="difficulty";%s</script>'%(GlobalTools.webscript)
	
	
	level_order=[]
	songs={}
	try:
		with open(GlobalTools.dbdir+table+'_level_order.json','r') as fp:
			level_order = json.loads(fp.read().decode('utf-8'))
		with open(GlobalTools.dbdir+table+'_body.json','r') as fp:
			songs = json.loads(fp.read().decode('utf-8'))
		loaded='<div id="loaded" style="display: none">'+generateFilter(level_order)+generateTable(level_order,songs)+'<div class="popup"><div class="ESC-button">[ESC] Close</div><div class="popup-title1 small-title"></div><div class="popup-title2 small-title"></div><div class="popup-content"></div></div></div>'
	except Exception as e:
		loaded='<div id="loaded" style="display: none"><div class="small-title">Failed to load data.</div><div class="popup"><div class="ESC-button">[ESC] Close</div><div class="popup-title1 small-title"></div><div class="popup-title2 small-title"></div><div class="popup-content"></div></div></div>'
	
	newContents='<div id="myextend">'+pre_def+title+loading+loaded+post_def+'</div>'
	
	body=WebpageExtensionHandler.modifyContents(body,True,True,newContents)
	
	return res,body