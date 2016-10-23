#coding: utf-8
import threading
from urlparse import urlparse, parse_qsl
from SocketServer import ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import DPISocket
import LR2RequestHandler
import WebpageExtensionHandler
import DifficultyPageHandler
import RecentPageHandler
import RankingRequestHandler
import ChallengePageHandler
import ChallengeRequestHandler

class LR2RRServer(BaseHTTPRequestHandler):
	def do_all(self):
		
		temp = urlparse(self.path)
		req_url = temp.path
		req_body = self.rfile.read(int(self.headers.getheader('content-length',0)))
		
		q_dict = {}
		for qq in parse_qsl(temp.query)+parse_qsl(req_body):
			q_dict[qq[0]]=qq[1]
		
		result=''
		resultBody=''
		hasExtended=False
		
		if req_url == '/~lavalse/LR2IR/2/getrankingxml.cgi':
			result, resultBody = LR2RequestHandler.handleRanking(q_dict)
		elif req_url == '/~lavalse/LR2IR/search.cgi' and 'mode' in q_dict:
			if q_dict['mode']=='difficulty':
				result, resultBody = DifficultyPageHandler.handleDifficultyPage(self.headers,q_dict)
				hasExtended=True
			elif q_dict['mode']=='challenge':
				result, resultBody = ChallengePageHandler.handleChallengePage(self.headers)
				hasExtended=True
			elif q_dict['mode']=='recent':
				result, resultBody = RecentPageHandler.handleRecentPage(self.headers)
				hasExtended=True
		elif req_url == '/~lavalse/LR2IR/ranking.cgi':
			result, resultBody = RankingRequestHandler.handleRankingRequest(q_dict)
		elif req_url == '/~lavalse/LR2IR/challenge.cgi':
			result, resultBody = ChallengeRequestHandler.handleChallengeRequest(q_dict)
		
		if not result:
			sock = DPISocket.DPISocket(self.command,self.path,self.request_version)
			sock.setMsg(self.headers)
			sock.setBody(req_body)
			result, resultBody = sock.sendAndReceive()
		
		if req_url == '/~lavalse/LR2IR/2/login.cgi':
			resultBody = LR2RequestHandler.handleLogin(resultBody)
		elif req_url == '/~lavalse/LR2IR/2/score.cgi':
			LR2RequestHandler.handleScore(q_dict)
		elif req_url == '/~lavalse/LR2IR/search.cgi' and not hasExtended:
			resultBody = WebpageExtensionHandler.modifyContents(resultBody)
		
		
		self.send_response(result.status,result.reason)
		
		if 'connection' in result.msg.keys():
			result.msg.__delitem__('connection')
		if 'keep-alive' in result.msg.keys():
			result.msg.__delitem__('keep-alive')
		result.msg['content-length'] = str(len(resultBody))
		for hdr in result.msg:
			self.send_header(hdr,result.msg[hdr])
		self.end_headers()
		
		self.wfile.write(resultBody)
		
		return
	def log_message(self, format, *args):
		# need to overwrite the original log_message function
		# or all the incoming requests will output sth to console
		return
	do_GET  = do_all
	do_POST = do_all
	do_HEAD = do_all
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""

def startServer():
	# needs a multithreaded server for handling multiple requests in same time
	server = ThreadedHTTPServer(('www.dream-pro.info', 80), LR2RRServer)
	server.daemon_threads=True
	server.serve_forever()