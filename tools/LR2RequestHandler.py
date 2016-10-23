#coding: utf-8
import threading

import GlobalTools
import RankingGenerator
import RivalUpdater
import ScoreUpdater

def handleLogin(body):
	newBody=body
	tokens=newBody.split(',')
	if tokens[0] in ['#OK','#B1','#B2','#B3','#NEW'] and len(tokens)>1:
		tokens[0]='#OK'
		pid=tokens[1]
		if pid.isdigit():
			thr=threading.Thread(target=RivalUpdater.updateRival,args=(pid,))
			thr.daemon=True
			thr.start()
		return ','.join(tokens)
	else:
		return newBody

def handleScore(q_dict):
	try:
		if not len(q_dict['songmd5'])==32: return '',''
		
		score={
			'hash' : q_dict['songmd5'],
			'id' : q_dict['id'],
			'clear' : q_dict['clear'],
			'notes' : q_dict['totalnotes'],
			'combo' : q_dict['maxcombo'],
			'pg' : q_dict['pg'],
			'gr' : q_dict['gr'],
			'minbp' : q_dict['minbp']
		}
		ScoreUpdater.updateScore(score)
	except Exception as e: pass

def handleRanking(q_dict):
	res=GlobalTools.SimpleHTTPResponse()
	body=''
	try:
		if not len(q_dict['songmd5'])==32: return '',''
		body='#'+RankingGenerator.generateRankingXML(q_dict['songmd5'],True)
	except Exception as e: pass
	
	return res,body