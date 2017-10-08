#coding: utf-8
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


def generateTable(songs):
	table='''
		<table><thead><tr>
			<th class="level leftborder2">#</th>
			<th class="title">Title</th>
			<th class="lamp leftborder">L</th>
			<th class="bp">BP</th>
			<th class="score">Score</th>
			<th class="ranking rightborder">Ranking</th>
			<th class="playedN rightborder2">Played</th>
		</tr></thead><tbody>
	'''
	trs=[]
	cnt=0
	for song in songs:
		cs=getPlayerScore(song['hash'])
		cnt+=1
		
		tr=''
		tr+='<tr>'
		tr+='<td class="level leftborder">'+str(cnt)+'</td>'
		tr+='<td class="title"><a target="_blank" href="http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=ranking&amp;bmsmd5='+song['hash']+'">'+GlobalTools.convertHTMLEntities(song['title'])+'</a></td>'
		tr+='<td class="lamp leftborder'+cs['lamp_class']+'"><span style="display:none">'+cs['lamp']+'</span></td>'
		tr+='<td class="bp'+cs['bp_class']+cs['lamp_class']+'">'+cs['bp']+'</td>'
		tr+='<td class="score'+cs['lamp_class']+'"><div class="'+cs['score_class']+'" style="width:'+cs['score_rate']+'">&nbsp;'+cs['score_rate']+cs['score']+'</div></td>'
		tr+='<td class="ranking rightborder'+cs['ranking_class']+cs['lamp_class']+'">'+cs['ranking']+'</td>'
		tr+='<td class="playedN rightborder'+cs['playedN_class']+'" hash="'+song['hash']+'">'+cs['playedN']+'</td>'
		tr+='</tr>'
		trs.append(tr)
	if cnt==0: table='<div class="small-title">No recent records.</div>'
	else: table+= ''.join(trs)+'</tbody></table>'
	return table

def handleRecentPage(headers):
	sock=DPISocket.DPISocket('GET','/~lavalse/LR2IR/search.cgi?mode=detail')
	sock.setMsg(headers)
	res,body=sock.sendAndReceive()
	
	songs={}
	with GlobalTools.dbLock:
		GlobalTools.cur.execute('''
			SELECT rt.hash AS hash, rt.title AS title, rt.lastupdate AS lastupdate
			FROM rivals AS rr INNER JOIN recent AS rt ON rr.id=rt.id
			WHERE rr.active=2
			ORDER BY rt.lastupdate DESC
		''')
		songs=GlobalTools.cur.fetchall()
	
	pre_def='''
		<script src="https://code.jquery.com/jquery-3.1.1.min.js"></script>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.27.8/js/jquery.tablesorter.min.js"></script>
		<style>'''+GlobalTools.webstyle+'''</style>
	'''
	title=u'<div class="big-title">最近の遊び記録</div>'
	loading='<div class="small-title" id="loading">Loading...</div>'
	post_def='<script>var mode="recent";'+GlobalTools.webscript+'</script>'
	
	try:
		loaded='<div id="loaded" style="display: none">'+generateTable(songs)+'<div class="popup"><div class="ESC-button">[ESC] Close</div><div class="popup-title1 small-title"></div><div class="popup-title2 small-title"></div><div class="popup-content"></div></div></div>'
	except Exception as e:
		loaded='<div id="loaded" style="display: none"><div class="small-title">Failed to load data.</div><div class="popup"><div class="ESC-button">[ESC] Close</div><div class="popup-title1 small-title"></div><div class="popup-title2 small-title"></div><div class="popup-content"></div></div></div>'
	
	newContents='<div id="myextend">'+pre_def+title+loading+loaded+post_def+'</div>'
	
	body=WebpageExtensionHandler.modifyContents(body,True,True,newContents)
	
	return res,body