#coding: utf-8
import json
import GlobalTools

def getRivalsScores(hash):
	with GlobalTools.dbLock:
		GlobalTools.cur.execute('''
			SELECT rr.name AS name, rr.id AS id, ss.clear AS clear, ss.notes AS notes, 
					ss.pg*2+ss.gr AS score, ss.minbp AS minbp, rr.active AS active
			FROM rivals AS rr INNER JOIN scores AS ss ON rr.id=ss.id
			WHERE rr.active>0 AND ss.hash=?
			ORDER BY score DESC
		''',(hash,))
		played=GlobalTools.cur.fetchall()
		GlobalTools.cur.execute('''
			SELECT name, id, 0 AS clear, 0 AS notes, 
					0 AS score, 0 AS minbp, active
			FROM rivals
			WHERE active>0 AND NOT id IN(
				SELECT id FROM scores WHERE hash=?
			)
		''',(hash,))
		notplayed=GlobalTools.cur.fetchall()
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
				else: rr['bpdiff']='-'
			
			
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
				else: rr['scorediff']='-'
			
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
	return result

def handleRankingRequest(q_dict):
	res=GlobalTools.SimpleHTTPResponse()
	
	if 'hash' in q_dict: scores=getRivalsScores(q_dict['hash'])
	else: scores=[]
	
	if len(scores)==0:
		rr='<div class="small-title">Failed to load data.</div>'
	else:
		try:
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
		except Exception as e: rr='<div class="small-title">Failed to load data.</div>'
	
	body=rr.encode('utf-8')
	return res,body