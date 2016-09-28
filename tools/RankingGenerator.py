#coding: utf-8
import GlobalTools
import sqlite3
import time

def generateRanking(hash,toPrint=True):
	conn = sqlite3.connect(GlobalTools.dbpath)
	conn.row_factory = sqlite3.Row
	cur = conn.cursor()
	cur.execute('''
		SELECT rr.name AS name, rr.id AS id, ss.clear AS clear, ss.notes AS notes, 
				ss.combo AS combo, ss.pg AS pg, ss.gr AS gr, ss.minbp AS minbp, rr.active AS active
		FROM rivals AS rr INNER JOIN scores AS ss ON rr.id=ss.id
		WHERE rr.active>0 AND ss.hash=?
	''',(hash,))
	played=cur.fetchall()
	cur.execute('''
		SELECT name, id, 0 AS clear, 0 AS notes, 
				0 AS combo, 0 AS pg, 0 AS gr, 0 AS minbp, active
		FROM rivals
		WHERE active>0 AND NOT id IN(
			SELECT id FROM scores WHERE hash=?
		)
	''',(hash,))
	notplayed=cur.fetchall()
	conn.close()
	
	scores=sorted(played+notplayed, key=(lambda score: (score['pg']*2+score['gr'])), reverse=True)
	
	body='<?xml version="1.0" encoding="shift_jis"?>\n'
	body+='<ranking>\n'
	for score in scores:
		
		# write the rival's score to log
		if toPrint:
			nameMessage=''
			clearMessage=''
			rankMessage=''
			exMessage=''
			rateMessage=''
			leftPad=''
			
			if score['clear']==0:
				clearMessage='NO'
			elif score['clear']==1:
				clearMessage='<font\tstyle="color:FireBrick">FA</font>'
			elif score['clear']==2:
				clearMessage='<font\tstyle="color:LimeGreen">EC</font>'
			elif score['clear']==3:
				clearMessage='<font\tstyle="color:Goldenrod">CL</font>'
			elif score['clear']==4:
				clearMessage='<font\tstyle="color:WhiteSmoke">HC</font>'
			else:
				clearMessage='<font\tstyle="color:Violet">FC</font>'
			
			ex=score['pg']*2+score['gr']
			exMessage='%5d'%(ex)
			
			total=score['notes']*2
			if clearMessage=='NO' : rankMessage='  F'
			elif ex*9>=total*9 : rankMessage='<font\tstyle="color:Tomato">MAX</font>'
			elif ex*9>=total*8 : rankMessage='<font\tstyle="color:Gold">AAA</font>'
			elif ex*9>=total*7 : rankMessage='<font\tstyle="color:PowderBlue"> AA</font>'
			elif ex*9>=total*6 : rankMessage='<font\tstyle="color:RoyalBlue">  A</font>'
			elif ex*9>=total*5 : rankMessage='  B'
			elif ex*9>=total*4 : rankMessage='  C'
			elif ex*9>=total*3 : rankMessage='  D'
			elif ex*9>=total*2 : rankMessage='  E'
			else : rankMessage='  F'
			
			rate=0.0
			if not clearMessage=='NO' :
				rate=float(ex)/float(total)*100.0
			rateMessage='%6.2f%%'%(rate)
			
			url='http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=mypage&playerid='+str(score['id'])
			name2=GlobalTools.convertHTMLEntities(score['name'])
			if score['active']==1 :
				nameMessage='<a\thref="'+url+'"\tstyle="color:LightGray;text-decoration:none">'+name2+'</a>'
			else :
				nameMessage='<a\thref="'+url+'"\tstyle="color:Khaki;text-decoration:none">'+name2+'</a>'
			
			width=GlobalTools.strWidth(score['name'])
			if width<10:
				leftPad=' '*(10-width)
			
			GlobalTools.logger.write( ' '+nameMessage+leftPad+' | '+clearMessage+' '+rankMessage+' '+rateMessage+' '+exMessage+'\n' )
		
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
	return body