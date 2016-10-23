#coding: utf-8
from urlparse import urlparse, parse_qs
import lxml.html
import lxml.etree
import DPISocket

def getRivals(id):
	pid=id
	rids=[]
	rids.append(pid)
	sock = DPISocket.DPISocket('GET','/~lavalse/LR2IR/search.cgi?mode=mypage&playerid=%s' % (pid) )
	res, body = sock.sendAndReceive()
	
	try:
		root=lxml.html.fromstring(body)
		for tr in root.find('.//table').findall('.//tr'):
			th=tr.find('th')
			if th.text==u'ライバル':
				for a in tr.find('td').findall('a'):
					rids.append( parse_qs(urlparse(a.attrib['href']).query)['playerid'][0] )
	except Exception as e: pass
	
	return rids

def getTitleAndArtist(hash):
	request_url='/~lavalse/LR2IR/search.cgi?mode=ranking&bmsmd5=%s' % (hash)
	
	title=''
	artist=''
	
	sock = DPISocket.DPISocket('GET', request_url)
	res, body = sock.sendAndReceive()
	
	try:
		root=lxml.html.fromstring(body)
		if root.find('.//h1') is not None :
			title=root.find('.//h1').text
		if root.find('.//h2') is not None :
			artist=root.find('.//h2').text
	except Exception as e: pass
	
	return title,artist