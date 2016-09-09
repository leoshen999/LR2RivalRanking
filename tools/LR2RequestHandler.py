#coding: utf-8
import Database
import GlobalTools
import WebpageParser
from httplib import HTTPMessage
from StringIO import StringIO
import RankingGenerator
import RivalUpdater
import ScoreUpdater

def handleLogin(q_dict):
	with Database.lock:
		GlobalTools.logger.write( '------- Update rival list --------\n' )
		
		pid=''
		rids=[]
		# parse the rival id list from the personal page of current player
		# if id not exists, the rival list should be empty
		if('id' in q_dict):
			pid = q_dict['id'][0]
			rids = WebpageParser.getRivals(pid)
		
		status=RivalUpdater.updateRival(pid,rids,True)
		if not status:
			GlobalTools.logger.write( '   Failed to update rival list    \n' )
		GlobalTools.logger.write( '----------------------------------\n' )
		GlobalTools.logger.write( '\n' )

def handleScore(q_dict):
	with Database.lock:
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


# a simple fake response for the result of getrankingxml.cgi
class SimpleHTTPResponse():
	def __init__(self):
		self.msg = HTTPMessage(StringIO())
		self.msg['content-type'] = 'text/plain'
		self.status = 200
		self.reason = 'OK'
def handleRanking(q_dict):
	with Database.lock:
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
		res=SimpleHTTPResponse()
		body='#'+RankingGenerator.generateRanking(hash,True)
		
		GlobalTools.logger.write( '----------------------------------\n' )
		GlobalTools.logger.write( '\n' )
		return res,body