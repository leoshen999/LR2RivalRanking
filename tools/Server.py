#coding: utf-8
import threading
from urlparse import urlparse, parse_qs
from SocketServer import ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import DPISocket
import LR2RequestHandler
import WebpageExtensionHandler
import GlobalTools

class LR2RRServer(BaseHTTPRequestHandler):
	def do_all(self):
		
		parsed_path = urlparse(self.path)
		self.req_body = self.rfile.read(int(self.headers.getheader('content-length',0)))
		
		q_dict_get=parse_qs(parsed_path.query)
		q_dict_post=parse_qs(self.req_body)
		
		result=''
		resultBody=''
		
		# getrankingxml.cgi: the result should be replaced with following:
		if parsed_path.path == '/~lavalse/LR2IR/2/getrankingxml.cgi':
			result, resultBody = LR2RequestHandler.handleRanking(q_dict_post)
		
		if GlobalTools.misc['webpageextension']=='True':
			# search.cgi: generate difficulty table
			if parsed_path.path == '/~lavalse/LR2IR/search.cgi' and 'difficultytable' in q_dict_get:
				result, resultBody=WebpageExtensionHandler.handleDifficultyTableSearch(self.headers,q_dict_get)
			# search.cgi: generate difficulty table
			if parsed_path.path == '/~lavalse/LR2IR/search.cgi' and 'difficultytablehash' in q_dict_get:
				result, resultBody=WebpageExtensionHandler.handleDifficultyTableHashSearch(q_dict_get)
		
		
		# send the original request to LR2IR for unhandled request type
		if result == '':
			sock = DPISocket.DPISocket(self.command,self.path,self.request_version)
			sock.setMsg(self.headers)
			sock.setBody(self.req_body)
			result, resultBody = sock.sendAndReceive()
		
		if GlobalTools.misc['webpageextension']=='True':
			# search.cgi: append difficulty table link to webpage
			if parsed_path.path == '/~lavalse/LR2IR/search.cgi' and 'difficultytable' not in q_dict_get and 'difficultytablehash' not in q_dict_get:
				resultBody=WebpageExtensionHandler.modifyContents(resultBody)
		
		# login.cgi: the rival list and scores should be updated
		if parsed_path.path == '/~lavalse/LR2IR/2/login.cgi':
			resultBody=LR2RequestHandler.handleLogin(resultBody)
		
		# score.cgi: update the database with the sent score
		if parsed_path.path == '/~lavalse/LR2IR/2/score.cgi':
			LR2RequestHandler.handleScore(q_dict_post)
		
		# return the result to client
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