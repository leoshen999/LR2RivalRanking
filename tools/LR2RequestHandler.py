#coding: utf-8
import GlobalTools
import WebpageParser
import threading

import RankingGenerator
import RivalUpdater
import ScoreUpdater

def handleLoginWithPid(pid):
	with GlobalTools.lock:
		GlobalTools.logger.write( '------- Update rival list --------\n' )
		rids = WebpageParser.getRivals(pid)
		status=RivalUpdater.updateRival(pid,rids,True)
		if not status:
			GlobalTools.logger.write( '   Failed to update rival list    \n' )
		GlobalTools.logger.write( '----------------------------------\n' )
		GlobalTools.logger.write( '\n' )
def handleLogin(body):
	newBody=body
	tokens=newBody.split(',')
	if tokens[0]=='#ERROR':
		return newBody
	tokens[0]='#OK'
	if len(tokens)>1:
		pid=tokens[1]
		if pid.isdigit():
			thr=threading.Thread(target=handleLoginWithPid,args=(pid,))
			thr.daemon=True
			thr.start()
	return ','.join(tokens)

def handleScore(q_dict):
	with GlobalTools.lock:
		GlobalTools.logger.write( '---------- Update score ----------\n' )
		
		# only handle the len==32 songmd5, or the score is not saved
		hash=q_dict['songmd5'][0]
		if not len(hash)==32:
			GlobalTools.logger.write( '         Unsupported md5          \n' )
			GlobalTools.logger.write( '----------------------------------\n' )
			GlobalTools.logger.write( '\n' )
			return
		
		# get song title and artist
		WebpageParser.printTitleAndArtist(hash)
		
		# write the score to database
		score={
			'hash' : q_dict['songmd5'][0],
			'id' : q_dict['id'][0],
			'clear' : q_dict['clear'][0],
			'notes' : q_dict['totalnotes'][0],
			'combo' : q_dict['maxcombo'][0],
			'pg' : q_dict['pg'][0],
			'gr' : q_dict['gr'][0],
			'minbp' : q_dict['minbp'][0]
		}
		status=ScoreUpdater.updateScore(score,True)
		
		if not status:
			GlobalTools.logger.write( '      Failed to update score      \n' )
		GlobalTools.logger.write( '----------------------------------\n' )
		GlobalTools.logger.write( '\n' )



def handleRanking(q_dict):
	with GlobalTools.lock:
		GlobalTools.logger.write( '----- Generate rival ranking -----\n' )
		
		# only handle the len==32 songmd5, or the score is not saved
		hash=q_dict['songmd5'][0]
		if not len(hash)==32:
			GlobalTools.logger.write( '         Unsupported md5          \n' )
			GlobalTools.logger.write( '----------------------------------\n' )
			GlobalTools.logger.write( '\n' )
			return '',''
		
		# get song title and artist
		WebpageParser.printTitleAndArtist(hash)
		
		# create a fake response
		res=GlobalTools.SimpleHTTPResponse()
		body='#'+RankingGenerator.generateRanking(hash,True)
		
		GlobalTools.logger.write( '----------------------------------\n' )
		GlobalTools.logger.write( '\n' )
		return res,body