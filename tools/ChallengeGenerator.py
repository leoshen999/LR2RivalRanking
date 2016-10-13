#coding: utf-8
import sqlite3
import urllib2
import json
import urllib
import datetime

import GlobalTools
import WebpageParser

def addChallenge(hash,id,name):
	url='https://www.csie.ntu.edu.tw/~b00902017/LR2RR/add.php?'
	q={}
	q['hash']=hash
	q['id_to']=id
	q['name_to']=name
	with GlobalTools.lock:
		conn = sqlite3.connect(GlobalTools.dbpath)
		conn.row_factory = sqlite3.Row
		cur = conn.cursor()
		cur.execute('''
			SELECT rr.name AS name, rr.id AS id, ss.clear AS clear, ss.notes AS notes, 
					ss.pg*2+ss.gr AS score, ss.minbp AS minbp
			FROM rivals AS rr INNER JOIN scores AS ss ON rr.id=ss.id
			WHERE rr.active=2 AND ss.hash=?
		''',(hash,))
		qq=cur.fetchall()[0]
		conn.close()
		q['id_from']=qq['id']
		q['name_from']=qq['name'].encode('utf-8')
		q['clear']=qq['clear']
		q['notes']=qq['notes']
		q['score']=qq['score']
		q['minbp']=qq['minbp']
	rt,ra=WebpageParser.getTitleAndArtist(hash,False)
	q['title']=rt.encode('utf-8')
	url+=urllib.urlencode(q)
	body=''
	if urllib2.urlopen(url).read() == 'OK':
		body='<table style="width:636px"><tbody><tr>'
		body+='<td class="title challengePopup2">'+GlobalTools.convertHTMLEntities(rt).encode('utf-8')+'</th>'
		body+='<td class="garbage challengePopup2">&gt;&gt;</th>'
		body+='<td class="name challengePopup2">'+q['name_to']+'</th>'
		body+='</tr></tbody></table>'
	else: body='<div class="tiny-title">Failed to send data.</div>'
	return body
def deleteChallenge(hash,id,direction):
	url='https://www.csie.ntu.edu.tw/~b00902017/LR2RR/delete.php?'
	q={}
	q['hash']=hash
	q['id2']=id
	q['direction']=direction
	with GlobalTools.lock:
		conn = sqlite3.connect(GlobalTools.dbpath)
		conn.row_factory = sqlite3.Row
		cur = conn.cursor()
		cur.execute('''
			SELECT id
			FROM rivals
			WHERE active=2
		''')
		qq=cur.fetchall()[0]
		q['id1']=qq['id']
		conn.close()
	url+=urllib.urlencode(q)
	body=''
	if urllib2.urlopen(url).read() == 'OK':
		body='<div class="tiny-title">Deleted successfully.</div>'
	else: body='<div class="tiny-title">Failed to send data.</div>'
	return body


def generateOneQueryRow(data):
	rr={}
	rr['title']=GlobalTools.convertHTMLEntities(data['title'])
	rr['name']=GlobalTools.convertHTMLEntities(data['name'])
	rr['id']=str(data['id'])
	rr['direction']='TO'
	rr['direction_class']=' TO'
	rr['clear']='NO PLAY'
	rr['clear_class']=' NO'
	rr['bp']=''
	rr['bp_class']=''
	rr['score']=''
	rr['score_class']=''
	rr['score_rate']=''
	rr['time']=''
	
	
	if data['direction']==1:
		rr['direction']='FROM'
		rr['direction_class']=' FROM'
	
	if data['clear']==5:
		rr['clear']='FULL COMBO'
		rr['clear_class']=' FC'
	elif data['clear']==4:
		rr['clear']='HARD CLEAR'
		rr['clear_class']=' HC'
	elif data['clear']==3:
		rr['clear']='CLEAR'
		rr['clear_class']=' CL'
	elif data['clear']==2:
		rr['clear']='EASY CLEAR'
		rr['clear_class']=' EC'
	elif data['clear']==1:
		rr['clear']='FAILED'
		rr['clear_class']=' FA'
	
	if data['minbp']==0:
		rr['bp_class']=' bp0'
	rr['bp']=str(data['minbp'])
	
	sc=data['score']
	total=data['notes']*2
	rr['score']='&nbsp;('+str(sc)+')'
	rr['score_class']=' BF'
	if sc*9>=total*9 : rr['score_class']=' MAX'
	elif sc*9>=total*8 : rr['score_class']=' AAA'
	elif sc*9>=total*7 : rr['score_class']=' AA'
	elif sc*9>=total*6 : rr['score_class']=' A'
	rr['score_rate']='%.2f%%' % (float(sc)/float(total)*100.0)
	
	rr['time']=datetime.datetime.fromtimestamp(data['lastupdate']).strftime('%Y-%m-%d %H:%M:%S')
	
	return rr

def queryChallenge():
	url='https://www.csie.ntu.edu.tw/~b00902017/LR2RR/query.php?'
	with GlobalTools.lock:
		conn = sqlite3.connect(GlobalTools.dbpath)
		conn.row_factory = sqlite3.Row
		cur = conn.cursor()
		cur.execute('''
			SELECT id
			FROM rivals
			WHERE active=2
		''')
		qq=cur.fetchall()[0]
		url+='id='+str(qq['id'])
		conn.close()
	datas=json.loads(urllib2.urlopen(url).read())
	divs=[]
	for data in list(reversed(datas)):
		rr=generateOneQueryRow(data)
		div='<div class="ch-box outer'+rr['direction_class']+'">'
		div+='<div class="ch-box title"><a target="_blank" href="http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=ranking&amp;bmsmd5='+data['hash']+'">'+rr['title']+'</a></div>'
		div+='<div class="ch-box namelabel">&nbsp;'+rr['direction']+':</div>'
		div+='<div class="ch-box name"><a target="_blank" href="http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=mypage&playerid='+rr['id']+'">'+rr['name']+'</a></div>'
		div+='<div class="ch-box clear'+rr['clear_class']+'">'+rr['clear']+'</div>'
		div+='<div class="ch-box bp'+rr['bp_class']+'">'+rr['bp']+' BP</div>'
		div+='<div class="ch-box score"><div class="'+rr['score_class']+'" style="width:'+rr['score_rate']+'">&nbsp;'+rr['score_rate']+rr['score']+'</div></div>'
		div+='<div class="ch-box time">'+rr['time']+'</div>'
		div+='<div class="ch-box delete" hash="'+data['hash']+'" rid="'+rr['id']+'" direction="'+rr['direction']+'">Delete</div>'
		div+='<div class="ch-box more" hash="'+data['hash']+'">More</div>'
		div+='<div class="ch-box line'+rr['direction_class']+'"></div>'
		div+='</div>'
		divs+=div
	divs=''.join(divs)
	if len(datas)==0 :divs='<div class="small-title">No challenge records.</div>'
	
	return divs.encode('utf-8')