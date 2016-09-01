#coding: utf-8
import Database
import DPISocket
import GlobalTools
import sqlite3
import lxml.html
import lxml.etree


def updateScore(q_dict):
	with Database.lock:
		GlobalTools.logger.write( '---------- Update score ----------\n' )
		
		songmd5=q_dict['songmd5'][0]
		if not len(songmd5)==32:
			GlobalTools.logger.write( ' Unsupported md5: score not saved \n' )
			GlobalTools.logger.write( '----------------------------------\n' )
			GlobalTools.logger.write( '\n' )
			return
		
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
		
		conn = sqlite3.connect(Database.path)
		conn.row_factory = sqlite3.Row
		cur = conn.cursor()
		try:
			cur.execute('''
				REPLACE INTO scores VALUES(?,?,?,?,?,?,?,?)
			''',(q_dict['songmd5'][0],q_dict['id'][0],q_dict['clear'][0],q_dict['totalnotes'][0],q_dict['maxcombo'][0],q_dict['pg'][0],q_dict['gr'][0],q_dict['minbp'][0]))
			conn.commit()
		except sqlite3.Error as er:
			conn.rollback()
			GlobalTools.logger.write( '      Failed to update score      \n' )
			GlobalTools.logger.write( '----------------------------------\n' )
			GlobalTools.logger.write( '\n' )
			return
		
		clear=''
		rank=''
		ex=''
		rate=''
		total=''
		if q_dict['clear'][0]=='0':
			clear='NOT PLAYED'
		elif q_dict['clear'][0]=='1':
			clear='<font\tstyle="color:FireBrick">  FAILED  </font>'
		elif q_dict['clear'][0]=='2':
			clear='<font\tstyle="color:LimeGreen">EASY CLEAR</font>'
		elif q_dict['clear'][0]=='3':
			clear='<font\tstyle="color:Goldenrod">  CLEAR   </font>'
		elif q_dict['clear'][0]=='4':
			clear='<font\tstyle="color:WhiteSmoke">HARD CLEAR</font>'
		else:
			clear='<font\tstyle="color:Violet">FULL COMBO</font>'
		
		ex=int(q_dict['pg'][0])*2+int(q_dict['gr'][0])
		total=int(q_dict['totalnotes'][0])*2
		if clear=='NOT PLAYED' : rank='  F'
		elif ex*9>=total*9 : rank='<font\tstyle="color:Tomato">MAX</font>'
		elif ex*9>=total*8 : rank='<font\tstyle="color:Gold">AAA</font>'
		elif ex*9>=total*7 : rank='<font\tstyle="color:PowderBlue"> AA</font>'
		elif ex*9>=total*6 : rank='<font\tstyle="color:RoyalBlue">  A</font>'
		elif ex*9>=total*5 : rank='  B'
		elif ex*9>=total*4 : rank='  C'
		elif ex*9>=total*3 : rank='  D'
		elif ex*9>=total*2 : rank='  E'
		else : rank='  F'
		ex='%5d'%(ex)
		
		if clear=='NOT PLAYED' : rate=0.0
		else: rate=float(ex)/float(total)*100.0
		rate='%6.2f%%'%(rate)
		
		
		GlobalTools.logger.write('  '+clear+' | '+rank+' '+rate+' '+ex+'  \n')
		
		conn.close()
		GlobalTools.logger.write( '----------------------------------\n' )
		GlobalTools.logger.write( '\n' )
		return