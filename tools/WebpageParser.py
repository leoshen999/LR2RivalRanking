#coding: utf-8
from urlparse import urlparse, parse_qs
import lxml.html
import lxml.etree
import DPISocket
import GlobalTools

def getRivals(id):
	pid=id
	rids=[]
	rids.append(pid)
	sock = DPISocket.DPISocket('GET','/~lavalse/LR2IR/search.cgi?mode=mypage&playerid=%s' % (pid) )
	res, body = sock.sendAndReceive()
	if res is False: return rids
	
	root=lxml.html.fromstring(body)
	table=root.find('.//table')
	if table is not None :
		for tr in table.findall('.//tr'):
			th=tr.find('th')
			if th is not None and th.text==u'ライバル':
				for a in tr.find('td').findall('a'):
					rids.append( parse_qs(urlparse(a.attrib['href']).query)['playerid'][0] )
	return rids



def printTitleAndArtist(hash):
	request_url='/~lavalse/LR2IR/search.cgi?mode=ranking&bmsmd5=%s' % (hash)
	full_url='http://www.dream-pro.info'+request_url
	
	sock = DPISocket.DPISocket('GET', request_url)
	res, body = sock.sendAndReceive()
	if res is False: return
	
	root=lxml.html.fromstring(body)
	if root.find('.//h1') is not None :
		title=root.find('.//h1').text
		if title is not None:
			width=GlobalTools.strWidth(title)
			leftPad=''
			rightPad=''
			if(width<=34):
				leftPad=' '*((34-width)/2)
				rightPad=' '*(34-width-len(leftPad))
			else:
				title=GlobalTools.strTruncateTo34(title)
			title=GlobalTools.convertHTMLEntities(title)
			GlobalTools.logger.write( leftPad+'<a\thref="'+full_url+'"\tstyle="color:LightGray;text-decoration:none">'+title+'</a>'+rightPad+'\n' )
	if root.find('.//h2') is not None :
		artist=root.find('.//h2').text
		if artist is not None:
			width=GlobalTools.strWidth(artist)
			leftPad=''
			rightPad=''
			if(width<=34):
				leftPad=' '*((34-width)/2)
				rightPad=' '*(34-width-len(leftPad))
			else:
				artist=GlobalTools.strTruncateTo34(artist)
			artist=GlobalTools.convertHTMLEntities(artist)
			GlobalTools.logger.write( leftPad+'<a\thref="'+full_url+'"\tstyle="color:LightGray;text-decoration:none">'+artist+'</a>'+rightPad+'\n' )