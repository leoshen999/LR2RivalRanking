#coding: utf-8
import sqlite3
import win32api
import json

import GlobalTools

class DifficultyGenerator():
	def __init__(self):
		pass
	def getPlayerScore(self,hash,cur):
		cur.execute('''
			SELECT rr.name AS name, rr.id AS id, ss.clear AS clear, ss.notes AS notes, 
					ss.pg*2+ss.gr AS score, ss.minbp AS minbp, rr.active AS active
			FROM rivals AS rr INNER JOIN scores AS ss ON rr.id=ss.id
			WHERE rr.active>0 AND ss.hash=?
			ORDER BY score DESC
		''',(hash,))
		played=cur.fetchall()
		
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
	def getRivalsScores(self,hash,cur):
		cur.execute('''
			SELECT rr.name AS name, rr.id AS id, ss.clear AS clear, ss.notes AS notes, 
					ss.pg*2+ss.gr AS score, ss.minbp AS minbp, rr.active AS active
			FROM rivals AS rr INNER JOIN scores AS ss ON rr.id=ss.id
			WHERE rr.active>0 AND ss.hash=?
			ORDER BY score DESC
		''',(hash,))
		played=cur.fetchall()
		cur.execute('''
			SELECT name, id, 0 AS clear, 0 AS notes, 
					0 AS score, 0 AS minbp, active
			FROM rivals
			WHERE active>0 AND NOT id IN(
				SELECT id FROM scores WHERE hash=?
			)
		''',(hash,))
		notplayed=cur.fetchall()
		scores=played+notplayed
		
		p_lamp=0
		p_score=0
		p_bp=0
		for score in scores:
			if score['active'] == 2:
				p_lamp=score['clear']
				p_score=score['score']
				p_bp=score['minbp']
				break
		
		result=[]
		prev_score=99999999
		prev_ranking=0
		cnt=0
		for score in scores:
			cnt+=1
			rr={}
			rr['id']=str(score['id'])
			rr['name']= GlobalTools.convertHTMLEntities(score['name'])
			rr['name_class']=''
			if score['active']==2 : rr['name_class']=' pid'
			
			rr['lamp']=str(score['clear'])
			rr['lamp_class']=' NO'
			if score['clear'] == 1 : rr['lamp_class']=' FA'
			elif score['clear'] == 2 : rr['lamp_class']=' EC'
			elif score['clear'] == 3 : rr['lamp_class']=' CL'
			elif score['clear'] == 4 : rr['lamp_class']=' HC'
			elif score['clear'] == 5 : rr['lamp_class']=' FC'
			
			rr['challenge']=''
			rr['challenge_class']=''
			if p_lamp > 0 and score['active']!=2:
				rr['challenge']='+'
				rr['challenge_class']=' add'
			
			rr['bp']=''
			rr['bp_class']=''
			rr['bpdiff']=''
			rr['bpdiff_class']=''
			rr['score']=''
			rr['score_class']=''
			rr['score_rate']=''
			rr['scorediff']=''
			rr['scorediff_class']=''
			rr['ranking']=''
			rr['ranking_class']=''
			if score['clear'] > 0:
				rr['bp']=str(score['minbp'])
				if score['minbp']==0 : rr['bp_class']=' bp0'
				
				if p_lamp > 0:
					temp=p_bp-score['minbp']
					rr['bpdiff']=str(temp)
					rr['bpdiff_class']=' TIE'
					if temp > 0 :
						rr['bpdiff_class']=' LOSE'
						rr['bpdiff']='+'+rr['bpdiff']
					elif temp < 0 : rr['bpdiff_class']=' WIN'
				
				
				sc=score['score']
				total=score['notes']*2
				rr['score']='&nbsp;('+str(sc)+')'
				rr['score_class']=' BF'
				if sc*9>=total*9 : rr['score_class']=' MAX'
				elif sc*9>=total*8 : rr['score_class']=' AAA'
				elif sc*9>=total*7 : rr['score_class']=' AA'
				elif sc*9>=total*6 : rr['score_class']=' A'
				rr['score_rate']='%.2f%%' % (float(sc)/float(total)*100.0)
				
				if p_lamp > 0:
					temp=p_score-sc
					rr['scorediff']=str(temp)
					rr['scorediff_class']=' TIE'
					if temp > 0 :
						rr['scorediff_class']=' WIN'
						rr['scorediff']='+'+rr['scorediff']
					elif temp < 0 : rr['scorediff_class']=' LOSE'
				
				temp=sc - prev_score
				if temp < 0 :
					prev_ranking=cnt
					prev_score=sc
				rr['ranking']=str(prev_ranking)
				if prev_ranking == 1: rr['ranking_class']=' TOP1'
				elif prev_ranking == 2: rr['ranking_class']=' TOP2'
				elif prev_ranking == 3: rr['ranking_class']=' TOP3'
			else: rr['lamp']=''
			result.append(rr)
		return result,len(played)
	def generateRecent(self):
		loading='<div class="small-title" id="loading">Loading...</div>'
		
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
		songs=[]
		with GlobalTools.lock:
			conn = sqlite3.connect(GlobalTools.dbpath)
			conn.row_factory = sqlite3.Row
			cur = conn.cursor()
			cur.execute('''
				SELECT rt.hash AS hash, rt.title AS title, rt.lastupdate AS lastupdate
				FROM rivals AS rr INNER JOIN recent AS rt ON rr.id=rt.id
				WHERE rr.active=2
				ORDER BY rt.lastupdate DESC
			''')
			songs=cur.fetchall()
			cnt=0
			for song in songs:
				cs=self.getPlayerScore(song['hash'],cur)
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
			conn.close()
		if len(songs)==0: table='<div class="small-title">No recent records.</div>'
		else: table+= ''.join(trs)+'</tbody></table>'
		
		popup='<div class="popup"><div class="ESC-button">[ESC] Close</div><div class="popup-content"></div></div>'
		
		popup2='<div class="popup2"></div>'
		
		loaded='<div id="loaded" style="display: none">'+table+popup+popup2+'</div>'
		
		script='<script>var mode="recent";</script>'
		
		return loading+loaded+script
	def generateDifficulty(self,table):
		songs={}
		level_order=[]
		with open(GlobalTools.dbdir+table+'_level_order.json','r') as fp:
			level_order = json.loads(fp.read().decode('utf-8'))
		with open(GlobalTools.dbdir+table+'_body.json','r') as fp:
			songs = json.loads(fp.read().decode('utf-8'))
		
		
		loading='<div class="small-title" id="loading">Loading...</div>'
		
		
		temp=len(level_order)
		filter='<div class="ck">MinLV:<span style="position:relative;display:inline-block;width:45px;height:20px;">&nbsp;<select class="ck-select min-lv" onchange="resetFilterResult()">'
		for idx in range(temp):
			if idx==0: filter+='<option value="'+str(idx)+'" selected>'+level_order[idx]+'</option>'
			else: filter+='<option value="'+str(idx)+'">'+level_order[idx]+'</option>'
		filter+='</select></span> Filter:'
		
		for rank in [['MAX','MAX'],['AAA','AAA'],['AA','AA'],['A','A'],['BF','B-F']]:
			filter+='<label class="ck-button RANK '+rank[0]+'"><input type="checkbox" value="'+rank[0]+'" checked onchange="resetFilterResult()"><span>'+rank[1]+'</span></label>'
		filter+=' '
		
		for clear in [['FC','FULLCOMBO'],['HC','HARD'],['CL','NORMAL'],['EC','EASY'],['FA','FAILED'],['NO','NOPLAY']]:
			filter+='<label class="ck-button CLEAR '+clear[0]+'"><input type="checkbox" value="'+clear[0]+'" checked onchange="resetFilterResult()"><span>'+clear[1]+'</span></label>'
		
		filter+='<br>MaxLV:<span style="position:relative;display:inline-block;width:45px;height:20px;">&nbsp;<select class="ck-select max-lv" onchange="resetFilterResult()">'
		for idx in range(temp):
			if idx==temp-1: filter+='<option value="'+str(idx)+'" selected>'+level_order[idx]+'</option>'
			else: filter+='<option value="'+str(idx)+'">'+level_order[idx]+'</option>'
		filter+='</select></span> Status:'
		
		for rank in ['MAX','AAA','AA','A','BF']:
			filter+='<span class="ck-status RANK '+rank+'"></span>'
		filter+=' '
		for clear in ['FC','HC','CL','EC','FA','NO']:
			filter+='<span class="ck-status CLEAR '+clear+'"></span>'
		filter+='</div>'
		
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
		with GlobalTools.lock:
			conn = sqlite3.connect(GlobalTools.dbpath)
			conn.row_factory = sqlite3.Row
			cur = conn.cursor()
			for hash,song in songs.iteritems():
				cs=self.getPlayerScore(hash,cur)
				
				tr=''
				tr+='<tr class="song-tr'+cs['lamp_class']+cs['score_class']+'" hidden-level="'+str(level_order.index(song[0]))+'">'
				tr+='<td class="level leftborder">'+song[0]+'</td>'
				tr+='<td class="title"><a target="_blank" href="http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=ranking&amp;bmsmd5='+hash+'">'+GlobalTools.convertHTMLEntities(song[1])+'</a></td>'
				tr+='<td class="lamp leftborder'+cs['lamp_class']+'"><span style="display:none">'+cs['lamp']+'</span></td>'
				tr+='<td class="bp'+cs['bp_class']+cs['lamp_class']+'">'+cs['bp']+'</td>'
				tr+='<td class="score'+cs['lamp_class']+'"><div class="'+cs['score_class']+'" style="width:'+cs['score_rate']+'">&nbsp;'+cs['score_rate']+cs['score']+'</div></td>'
				tr+='<td class="ranking rightborder'+cs['ranking_class']+cs['lamp_class']+'">'+cs['ranking']+'</td>'
				tr+='<td class="playedN rightborder'+cs['playedN_class']+'" hash="'+hash+'">'+cs['playedN']+'</td>'
				tr+='</tr>'
				trs.append(tr)
			conn.close()
		table+= ''.join(trs)+'</tbody></table>'
		
		popup='<div class="popup"><div class="ESC-button">[ESC] Close</div><div class="popup-content"></div></div>'
		
		popup2='<div class="popup2"></div>'
		
		loaded='<div id="loaded" style="display: none">'+filter+table+popup+popup2+'</div>'
		
		lvs='['
		for level in level_order: lvs+='"'+level+'",'
		lvs+=']'
		script='<script>var level_order='+lvs+';var mode="difficulty";</script>'
		
		return loading+loaded+script
	def generatePopup(self,level,title,hash):
		result='<div class="small-title">'+level.decode('utf8')+'<a target="_blank" href="http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=ranking&amp;bmsmd5='+hash+'">'+GlobalTools.convertHTMLEntities(title.decode('utf8'))+'</a></div>'
		
		with GlobalTools.lock:
			conn = sqlite3.connect(GlobalTools.dbpath)
			conn.row_factory = sqlite3.Row
			cur = conn.cursor()
			scores,playedN=self.getRivalsScores(hash,cur)
			conn.close()
			
			rr='<table style="width:465px">'
			rr+='''<thead>
					<tr>
						<th class="ranking leftborder2">#</th>
						<th class="name">Name</th>
						<th class="lamp leftborder">L</th>
						<th class="bp">BP</th>
						<th class="bpdiff">Diff</th>
						<th class="score">Score</th>
						<th class="scorediff rightborder">Diff</th>
						<th class="challenge rightborder2">Ch</th>
					</tr>
				</thead>'''
			rr+='<tbody>'
			for s in scores:
				rr+='<tr>'
				rr+='<td class="ranking leftborder'+s['ranking_class']+'">'+s['ranking']+'</td>'
				rr+='<td class="name'+s['name_class']+'"><a target="_blank" href="http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=mypage&playerid='+s['id']+'">'+s['name']+'</a></td>'
				rr+='<td class="lamp leftborder'+s['lamp_class']+'"><span style="display:none">'+s['lamp']+'</span></td>'
				rr+='<td class="bp'+s['bp_class']+s['lamp_class']+'">'+s['bp']+'</td>'
				rr+='<td class="bpdiff'+s['bpdiff_class']+s['lamp_class']+'">'+s['bpdiff']+'</td>'
				rr+='<td class="score'+s['lamp_class']+'"><div class="'+s['score_class']+'" style="width:'+s['score_rate']+'">&nbsp;'+s['score_rate']+s['score']+'</div></td>'
				rr+='<td class="scorediff rightborder'+s['scorediff_class']+s['lamp_class']+'">'+s['scorediff']+'</td>'
				rr+='<td class="challenge rightborder'+s['challenge_class']+'" rid="'+s['id']+'">'+s['challenge']+'</td>'
				rr+='</tr>'
			rr+='</tbody></table>'
		result+=rr
		return result
difficultyGenerator=DifficultyGenerator()








