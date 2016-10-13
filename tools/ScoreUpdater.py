#coding: utf-8
import time
import sqlite3
import GlobalTools

# caution: score entries are all in string form
def updateScore(score,title,toPrint=True):
	conn = sqlite3.connect(GlobalTools.dbpath)
	conn.row_factory = sqlite3.Row
	cur = conn.cursor()
	try:
		cur.execute('''
			REPLACE INTO scores VALUES(?,?,?,?,?,?,?,?)
		''',(score['hash'],score['id'],score['clear'],score['notes'],score['combo'],score['pg'],score['gr'],score['minbp']))
		current_time=int(time.time())
		cur.execute('''
			REPLACE INTO recent VALUES(?,?,?,?)
		''',(score['hash'],score['id'],title,current_time))
		cur.execute('''
			DELETE FROM recent
			WHERE id=? AND hash NOT IN(
				SELECT hash FROM recent WHERE id=? ORDER BY lastupdate DESC LIMIT 30
			)
		''',(score['id'],score['id']))
		conn.commit()
	except sqlite3.Error as er:
		conn.rollback()
		conn.close()
		return False
	conn.close()
	
	# write the score to log
	if toPrint:
		clearMessage=''
		rankMessage=''
		exMessage=''
		rateMessage=''
		
		if score['clear']=='0':
			clearMessage='NOT PLAYED'
		elif score['clear']=='1':
			clearMessage='<font\tstyle="color:FireBrick">  FAILED  </font>'
		elif score['clear']=='2':
			clearMessage='<font\tstyle="color:LimeGreen">EASY CLEAR</font>'
		elif score['clear']=='3':
			clearMessage='<font\tstyle="color:Goldenrod">  CLEAR   </font>'
		elif score['clear']=='4':
			clearMessage='<font\tstyle="color:WhiteSmoke">HARD CLEAR</font>'
		else:
			clearMessage='<font\tstyle="color:Violet">FULL COMBO</font>'
		
		ex=int(score['pg'])*2+int(score['gr'])
		exMessage='%5d'%(ex)
		
		total=int(score['notes'])*2
		if clearMessage=='NOT PLAYED' : rankMessage='  F'
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
		if not clearMessage=='NOT PLAYED' :
			rate=float(ex)/float(total)*100.0
		rateMessage='%6.2f%%'%(rate)
		
		GlobalTools.logger.write('  '+clearMessage+' | '+rankMessage+' '+rateMessage+' '+exMessage+'  \n')
	
	return True