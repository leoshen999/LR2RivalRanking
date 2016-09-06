#coding: utf-8
import Database
import DPISocket
import GlobalTools
from httplib import HTTPMessage
from StringIO import StringIO
import sqlite3
import time
import lxml.html
import lxml.etree

# a simple fake response for the result of getrankingxml.cgi
class SimpleHTTPResponse():
	def __init__(self):
		self.msg = HTTPMessage(StringIO())
		self.status = 200
		self.reason = 'OK'

	def setStatus(self,status):
		self.status = int(status)

	def setReason(self, reason):
		self.reason = reason


def generateRivalRanking(q_dict):
	with Database.lock:
		GlobalTools.logger.write( '----- Generate rival ranking -----\n' )
		
		# only handle the len==32 songmd5, or use default ranking in case
		songmd5=q_dict['songmd5'][0]
		if not len(songmd5)==32:
			GlobalTools.logger.write( '         Unsupported md5          \n' )
			GlobalTools.logger.write( '----------------------------------\n' )
			GlobalTools.logger.write( '\n' )
			return '',''
		
		# get song title and artist
		sock = DPISocket.DPISocket('GET','/~lavalse/LR2IR/search.cgi?mode=ranking&bmsmd5=%s' % (songmd5) )
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
		
		# create a fake response
		res=SimpleHTTPResponse()
		res.msg['content-type'] = 'text/plain'
		
		conn = sqlite3.connect(Database.path)
		conn.row_factory = sqlite3.Row
		cur = conn.cursor()
		
		cur.execute('''
			SELECT rr.name AS name, rr.id AS id, ss.clear AS clear, ss.notes AS notes, 
					ss.combo AS combo, ss.pg AS pg, ss.gr AS gr, ss.minbp AS minbp, rr.active AS active
			FROM rivals AS rr INNER JOIN scores AS ss ON rr.id=ss.id
			WHERE rr.active>0 AND ss.hash=?
		''',(songmd5,))
		played=cur.fetchall()
		cur.execute('''
			SELECT name, id, 0 AS clear, 0 AS notes, 
					0 AS combo, 0 AS pg, 0 AS gr, 0 AS minbp, active
			FROM rivals
			WHERE active>0 AND NOT id IN(
				SELECT id FROM scores WHERE hash=?
			)
		''',(songmd5,))
		notplayed=cur.fetchall()
		
		conn.close()
		
		# sort the result for a better display
		scores=sorted(played+notplayed, key=(lambda score: (score['pg']*2+score['gr'])), reverse=True)
		
		# create a fake xml body
		body='#<?xml version="1.0" encoding="shift_jis"?>\n'
		body+='<ranking>\n'
		for score in scores:
			
			# write the rival's score to log
			clear=''
			if score['clear']==0:
				clear='NO'
			elif score['clear']==1:
				clear='<font\tstyle="color:FireBrick">FA</font>'
			elif score['clear']==2:
				clear='<font\tstyle="color:LimeGreen">EC</font>'
			elif score['clear']==3:
				clear='<font\tstyle="color:Goldenrod">CL</font>'
			elif score['clear']==4:
				clear='<font\tstyle="color:WhiteSmoke">HC</font>'
			else:
				clear='<font\tstyle="color:Violet">FC</font>'
			ex=score['pg']*2+score['gr']
			total=score['notes']*2
			rank=''
			if clear=='NO' : rank='  F'
			elif ex*9>=total*9 : rank='<font\tstyle="color:Tomato">MAX</font>'
			elif ex*9>=total*8 : rank='<font\tstyle="color:Gold">AAA</font>'
			elif ex*9>=total*7 : rank='<font\tstyle="color:PowderBlue"> AA</font>'
			elif ex*9>=total*6 : rank='<font\tstyle="color:RoyalBlue">  A</font>'
			elif ex*9>=total*5 : rank='  B'
			elif ex*9>=total*4 : rank='  C'
			elif ex*9>=total*3 : rank='  D'
			elif ex*9>=total*2 : rank='  E'
			else : rank='  F'
			if clear=='NO' : rate=0.0
			else: rate=float(ex)/float(total)*100.0
			leftPad=''
			width=GlobalTools.strWidth(score['name'])
			if width<10:
				leftPad=' '*(10-width)
			score_message=' | %s %s %6.2f%% %5d'%(clear,rank,rate,ex)
			if score['active']==1 :
				name='<font\tstyle="color:LightGray">'+score['name']+'</font>'
			else :
				name='<font\tstyle="color:Khaki">'+score['name']+'</font>'
			GlobalTools.logger.write( ' '+name+leftPad+score_message+'\n' )
			
			# append to result xml
			body+='\t<score>\n'
			body+='\t\t<name>%s</name>\n' % score['name']
			body+='\t\t<id>%d</id>\n' % score['id']
			body+='\t\t<clear>%d</clear>\n' % score['clear']
			body+='\t\t<notes>%d</notes>\n' % score['notes']
			body+='\t\t<combo>%d</combo>\n' % score['combo']
			body+='\t\t<pg>%d</pg>\n' % score['pg']
			body+='\t\t<gr>%d</gr>\n' % score['gr']
			body+='\t\t<minbp>%d</minbp>\n' % score['minbp']
			body+='\t</score>\n'
			
			
		body+='</ranking>\n'
		body+='<lastupdate>%s</lastupdate>' % time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(int(time.time())))
		body=body.encode('cp932')
		GlobalTools.logger.write( '----------------------------------\n' )
		GlobalTools.logger.write( '\n' )
		return res,body