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
	root=lxml.html.fromstring(body)
	table=root.find('.//table')
	if table is not None :
		for tr in table.findall('.//tr'):
			if tr.find('th').text==u'ライバル':
				for a in tr.find('td').findall('a'):
					rids.append( parse_qs(urlparse(a.attrib['href']).query)['playerid'][0] )
	return rids



def printTitleAndArtist(hash):
	sock = DPISocket.DPISocket('GET','/~lavalse/LR2IR/search.cgi?mode=ranking&bmsmd5=%s' % (hash) )
	res, body = sock.sendAndReceive()
	root=lxml.html.fromstring(body)
	if root.find('.//h1') is not None :
		title=root.find('.//h1').text
		width=GlobalTools.strWidth(title)
		leftPad=''
		rightPad=''
		if(width<=34):
			leftPad=' '*((34-width)/2)
			rightPad=' '*(34-width-len(leftPad))
		else:
			title=GlobalTools.strTruncateTo34(title)
		GlobalTools.logger.write( leftPad+'<font\tstyle="color:LightGray">'+title+'</font>'+rightPad+'\n' )
	if root.find('.//h2') is not None :
		artist=root.find('.//h2').text
		width=GlobalTools.strWidth(artist)
		leftPad=''
		rightPad=''
		if(width<=34):
			leftPad=' '*((34-width)/2)
			rightPad=' '*(34-width-len(leftPad))
		else:
			artist=GlobalTools.strTruncateTo34(artist)
		GlobalTools.logger.write( leftPad+'<font\tstyle="color:LightGray">'+artist+'</font>'+rightPad+'\n' )