#coding: utf-8
from urlparse import urljoin
import lxml.html
import lxml.etree
import sqlite3
import win32api
import urllib2
import json
import io

import GlobalTools

class DifficultyGenerator():
	def __init__(self):
		
		self.style=''
		self.script=''
		if GlobalTools.is_exe():
			self.style= win32api.LoadResource(0, u'STYLE_CSS', 4)
			self.script= win32api.LoadResource(0, u'SRC_JS', 5)
		else:
			with open('style.css','r') as fp:
				self.style=fp.read()
			with open('src.js','r') as fp:
				self.script=fp.read()
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
		rr['lamp_class']=' td-NO'
		rr['bp']=''
		rr['bp_class']=''
		rr['score']=''
		rr['score_class']=''
		rr['score_rate']=''
		rr['ranking']=''
		rr['ranking_class']=''
		
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
				if temp == 1 : rr['lamp_class']=' td-FA'
				elif temp == 2 : rr['lamp_class']=' td-EC'
				elif temp == 3 : rr['lamp_class']=' td-CL'
				elif temp == 4 : rr['lamp_class']=' td-HC'
				elif temp == 5 : rr['lamp_class']=' td-FC'
				
				temp=pl['minbp']
				rr['bp']=str(temp)
				if temp==0 : rr['bp_class']=' td-bp0'
				
				temp=pl['score']
				total=pl['notes']*2
				rr['score']='&nbsp;('+str(temp)+')'
				rr['score_class']=' td-CF'
				if temp*9>=total*9 : rr['score_class']=' td-MAX'
				elif temp*9>=total*8 : rr['score_class']=' td-AAA'
				elif temp*9>=total*7 : rr['score_class']=' td-AA'
				elif temp*9>=total*6 : rr['score_class']=' td-A'
				elif temp*9>=total*5 : rr['score_class']=' td-B'
				rr['score_rate']='%.2f%%' % (float(temp)/float(total)*100.0)
				
				rr['ranking']=str(prev_ranking)
				if prev_ranking == 1:
					rr['ranking_class']=' td-TOP'
				break
		return rr,len(played)
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
			if score['active']==2 : rr['name_class']=' td-pid'
			
			rr['lamp']=str(score['clear'])
			rr['lamp_class']=' td-NO'
			if score['clear'] == 1 : rr['lamp_class']=' td-FA'
			elif score['clear'] == 2 : rr['lamp_class']=' td-EC'
			elif score['clear'] == 3 : rr['lamp_class']=' td-CL'
			elif score['clear'] == 4 : rr['lamp_class']=' td-HC'
			elif score['clear'] == 5 : rr['lamp_class']=' td-FC'
			
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
				if score['minbp']==0 : rr['bp_class']=' td-bp0'
				
				if p_lamp > 0:
					temp=p_bp-score['minbp']
					rr['bpdiff']=str(temp)
					rr['bpdiff_class']=' td-TIE'
					if temp > 0 :
						rr['bpdiff_class']=' td-LOSE'
						rr['bpdiff']='+'+rr['bpdiff']
					elif temp < 0 : rr['bpdiff_class']=' td-WIN'
				
				
				sc=score['score']
				total=score['notes']*2
				rr['score']='&nbsp;('+str(sc)+')'
				rr['score_class']=' td-CF'
				if sc*9>=total*9 : rr['score_class']=' td-MAX'
				elif sc*9>=total*8 : rr['score_class']=' td-AAA'
				elif sc*9>=total*7 : rr['score_class']=' td-AA'
				elif sc*9>=total*6 : rr['score_class']=' td-A'
				elif sc*9>=total*5 : rr['score_class']=' td-B'
				rr['score_rate']='%.2f%%' % (float(sc)/float(total)*100.0)
				
				if p_lamp > 0:
					temp=p_score-sc
					rr['scorediff']=str(temp)
					rr['scorediff_class']=' td-TIE'
					if temp > 0 :
						rr['scorediff_class']=' td-WIN'
						rr['scorediff']='+'+rr['scorediff']
					elif temp < 0 : rr['scorediff_class']=' td-LOSE'
				
				temp=sc - prev_score
				if temp < 0 :
					prev_ranking=cnt
					prev_score=sc
				rr['ranking']=str(prev_ranking)
				if prev_ranking == 1:
					rr['ranking_class']=' td-TOP'
			else: rr['lamp']=''
			result.append(rr)
		return result,len(played)
	def generateDifficulty(self,table):
		songs={}
		level_order=[]
		
		with io.open(GlobalTools.dbdir+table+'_level_order.json','r', encoding='utf-8') as fp:
			level_order = json.load(fp)
		with io.open(GlobalTools.dbdir+table+'_body.json','r', encoding='utf-8') as fp:
			songs = json.load(fp)
		
		
		temp=len(level_order)
		filter='<h5>LEVEL: <select class="min-lv" onchange="resetFilterResult()">'
		for idx in range(temp):
			if idx==0: filter+='<option value="'+str(idx)+'" selected>'+level_order[idx]+'</option>'
			else: filter+='<option value="'+str(idx)+'">'+level_order[idx]+'</option>'
		filter+='</select> to <select class="max-lv" onchange="resetFilterResult()">'
		for idx in range(temp):
			if idx==temp-1: filter+='<option value="'+str(idx)+'" selected>'+level_order[idx]+'</option>'
			else: filter+='<option value="'+str(idx)+'">'+level_order[idx]+'</option>'
		filter+='</select></h5>'
		
		filter+='<h5>RANK:&nbsp; '
		for rank in ['MAX','AAA','AA','A','B','C-F']:
			filter+='<label class="ck-button ck-'+rank+'"><input type="checkbox" class="RANK RANK-'+rank+'" value="'+rank+'" checked onchange="resetFilterResult()"><span>'+rank+'</span></label>'
		filter+='</h5>'
		
		filter+='<h5>CLEAR: '
		for clear in ['FULLCOMBO','HARD','NORMAL','EASY','FAILED','NOPLAY']:
			filter+='<label class="ck-button ck-'+clear+'"><input type="checkbox" class="CLEAR CLEAR-'+clear+'" value="'+clear+'" checked onchange="resetFilterResult()"><span>'+clear+'</span></label>'
		filter+='</h5>'
		
		
		body='''
			<script src="https://code.jquery.com/jquery-3.1.1.min.js"></script>
			<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.27.8/js/jquery.tablesorter.min.js"></script>
			<style>'''+self.style+'''</style>
			<div id="loaded" style="display: none">'''+filter+'''
			<table id="myTable" class="tablesorter">
				<thead>
					<tr>
						<th class="player th-level">Level</th>
						<th class="player th-title">Title</th>
						<th class="player th-lamp">L</th>
						<th class="player th-bp">BP</th>
						<th class="player th-score">Score</th>
						<th class="player th-ranking">Ranking</th>
						<th class="player th-playedN">Played</th>
					</tr>
				</thead><tbody>'''
		trs=[]
		
		with GlobalTools.lock:
			conn = sqlite3.connect(GlobalTools.dbpath)
			conn.row_factory = sqlite3.Row
			cur = conn.cursor()
			# cur.execute('''
				# SELECT id, name FROM rivals WHERE active=2
			# ''')
			# temp=cur.fetchall()
			# pid=temp[0]['id']
			# pname=temp[0]['name']
			
			for hash,song in songs.iteritems():
				cs,playedN=self.getPlayerScore(hash,cur)
				
				tr=''
				tr+='<tr class="song-tr" hidden-level="'+str(level_order.index(song[0]))+'">'
				tr+='<td class="td-level">'+song[0]+'</td>'
				tr+='<td class="td-title"><a target="_blank" href="http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=ranking&amp;bmsmd5='+hash+'">'+GlobalTools.convertHTMLEntities(song[1])+'</a></td>'
				tr+='<td class="player td-lamp'+cs['lamp_class']+'"><span class="not-show">'+cs['lamp']+'</span></td>'
				tr+='<td class="player td-bp'+cs['bp_class']+cs['lamp_class']+'">'+cs['bp']+'</td>'
				tr+='<td class="td-score'+cs['lamp_class']+'"><div class="player'+cs['score_class']+'" style="width:'+cs['score_rate']+'">&nbsp;'+cs['score_rate']+cs['score']+'</div></td>'
				tr+='<td class="player td-ranking'+cs['ranking_class']+cs['lamp_class']+'">'+cs['ranking']+'</td>'
				tr+='<td class="td-playedN" hash="'+hash+'">'+str(playedN)+'</td>'
				tr+='</tr>'
				trs.append(tr)
			conn.close()
		body+= ''.join(trs)
		
		lvs='['
		for level in level_order:
			lvs+='"'+level+'",'
		lvs+=']'
		body+='</tbody></table></div><div class="popup"><div class="ESC-button">[ESC] Close</div><div class="popup-content"></div></div><script>var level_order='+lvs+';'+self.script+'</script>'
		result=body
		
		
		
		return result
	def generatePopup(self,level,title,hash):
		result='<h6>'+level.decode('utf8')+'</h6><h6>'+GlobalTools.convertHTMLEntities(title.decode('utf8'))+'</h6>'
		
		with GlobalTools.lock:
			conn = sqlite3.connect(GlobalTools.dbpath)
			conn.row_factory = sqlite3.Row
			cur = conn.cursor()
			scores,playedN=self.getRivalsScores(hash,cur)
			conn.close()
			
			rr='<table style="width:444px">'
			rr+='''<thead>
					<tr>
						<th class="th-ranking">#</th>
						<th class="th-name">Name</th>
						<th class="th-lamp">L</th>
						<th class="th-bp">BP</th>
						<th class="th-bpdiff">diff</th>
						<th class="th-score">Score</th>
						<th class="th-scorediff">diff</th>
					</tr>
				</thead>'''
			rr+='<tbody>'
			for s in scores:
				rr+='<tr>'
				rr+='<td class="td-ranking td-leftmost'+s['ranking_class']+'">'+s['ranking']+'</td>'
				rr+='<td class="td-name"><a class="'+s['name_class']+'" target="_blank" href="http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=mypage&playerid='+s['id']+'">'+s['name']+'</a></td>'
				rr+='<td class="td-lamp'+s['lamp_class']+'"><span class="not-show">'+s['lamp']+'</span></td>'
				rr+='<td class="td-bp'+s['bp_class']+s['lamp_class']+'">'+s['bp']+'</td>'
				rr+='<td class="td-bpdiff'+s['bpdiff_class']+s['lamp_class']+'">'+s['bpdiff']+'</td>'
				rr+='<td class="td-score'+s['lamp_class']+'"><div class="'+s['score_class']+'" style="width:'+s['score_rate']+'">&nbsp;'+s['score_rate']+s['score']+'</div></td>'
				rr+='<td class="td-scorediff'+s['scorediff_class']+s['lamp_class']+'">'+s['scorediff']+'</td>'
				rr+='</tr>'
			rr+='</tbody></table>'
		result+=rr
		return result
difficultyGenerator=DifficultyGenerator()








