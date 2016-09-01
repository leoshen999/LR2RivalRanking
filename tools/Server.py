#coding: utf-8

import threading
from urlparse import urlparse, parse_qs
from SocketServer import ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import DPISocket
import RankingHandler
import LoginHandler
import ScoreHandler
import GlobalTools

class LR2RRServer(BaseHTTPRequestHandler):
	def do_all(self):
		
		parsed_path = urlparse(self.path)
		self.req_body = self.rfile.read(int(self.headers.getheader('content-length',0)))
		
		result=''
		resultBody=''
		
		if parsed_path.path == '/~lavalse/LR2IR/2/getrankingxml.cgi':
			result, resultBody = RankingHandler.generateRivalRanking(parse_qs(self.req_body))
		if parsed_path.path == '/~lavalse/LR2IR/2/login.cgi':
			thr=threading.Thread(target=LoginHandler.updateRivalList,args=(parse_qs(self.req_body),))
			thr.daemon=True
			thr.start()
		
		if result == '':
			sock = DPISocket.DPISocket(self.command,self.path,self.request_version)
			sock.setMsg(self.headers)
			sock.setBody(self.req_body)
			result, resultBody = sock.sendAndReceive()
		
		if parsed_path.path == '/~lavalse/LR2IR/2/login.cgi':
			if resultBody[0:3] in ['#B1','#B2','#B3'] :
				resultBody='#OK'+resultBody[3:]
		
		if parsed_path.path == '/~lavalse/LR2IR/2/score.cgi':
			ScoreHandler.updateScore(parse_qs(self.req_body))
		
		
		print result.status,result.reason
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
		return
	do_GET  = do_all
	do_POST = do_all
	do_HEAD = do_all
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""



def startServer():
	server = ThreadedHTTPServer(('www.dream-pro.info', 80), LR2RRServer)
	server.daemon_threads=True
	server.serve_forever()