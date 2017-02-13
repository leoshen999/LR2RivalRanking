#coding: utf-8

# thanks to GNQG/lr2irproxy for the original source code of DPISocket
# github: https://github.com/GNQG/lr2irproxy
# still not sure the necessity and detailed contents of this class

import socket
from httplib import HTTPMessage, HTTPResponse
from StringIO import StringIO
from zlib import decompress

import GlobalTools

ORIGINAL_IP = '115.179.53.238'

class DPISocket():
	def __init__(self, method, path, version='HTTP/1.1'):
		self.method = method.upper()
		self.path = path
		self.version = version
		self.msg = HTTPMessage(StringIO())
		self.body = ''

	def setHeader(self,key,val):
		self.msg[key]=val

	def setBody(self,body):
		self.body = body

	def setMsg(self,httpmsg):
		self.msg = httpmsg

	def __str__(self):
		self.msg['Host'] = 'www.dream-pro.info'
		if self.body:
			self.msg['content-length'] = str(len(self.body))
		else :
			self.msg['content-length'] = '0'
		s  = ''
		s += '%s %s %s\n' % (self.method, self.path, self.version)
		s += str(self.msg)
		s += '\n' # end of header
		s += self.body
		return s

	def sendAndReceive(self):
		try:
			sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			sock.connect((ORIGINAL_IP,80))
			sock.sendall(str(self))
		except:
			return GlobalTools.FailedHTTPResponse(),''
		
		res = HTTPResponse(sock)
		res.begin()
		res_body = res.read()
		res.close()
		
		if 'transfer-encoding' in res.msg:
			# httplib.HTTPResponse automatically concatenate chunked response
			# but do not delete 'transfer-encoding' header
			# so the header must be deleted
			res.msg.__delitem__('transfer-encoding')
		compmeth = res.msg.getheader('content-encoding','').lower()
		if compmeth and compmeth.find('identity') != 0 :
			# response body is compressed with some method
			offset = 0
			if compmeth.find('gzip') != -1:
				# if body is gziped, header offset value is 47
				# if not, offset value is 0
				# this server does not support sdch...
				offset += 47
			res_body = decompress(res_body,offset)
			res.msg['content-encoding'] = 'identity'

		return res, res_body
