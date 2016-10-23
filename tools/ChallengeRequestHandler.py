#coding: utf-8
import urllib2
import json
import urllib
import datetime

import GlobalTools
import WebpageParser


def addChallenge(hash,id,name):
	url='https://www.csie.ntu.edu.tw/~b00902017/LR2RR/add.php?'
	try:
		q={}
		q['hash']=hash
		q['id_to']=id
		q['name_to']=name
		with GlobalTools.dbLock:
			GlobalTools.cur.execute('''
				SELECT rr.name AS name, rr.id AS id, ss.clear AS clear, ss.notes AS notes, 
						ss.pg*2+ss.gr AS score, ss.minbp AS minbp
				FROM rivals AS rr INNER JOIN scores AS ss ON rr.id=ss.id
				WHERE rr.active=2 AND ss.hash=?
			''',(hash,))
			qq=GlobalTools.cur.fetchall()[0]
			q['id_from']=qq['id']
			q['name_from']=qq['name'].encode('utf-8')
			q['clear']=qq['clear']
			q['notes']=qq['notes']
			q['score']=qq['score']
			q['minbp']=qq['minbp']
		rt,ra=WebpageParser.getTitleAndArtist(hash)
		q['title']=rt.encode('utf-8')
		url+=urllib.urlencode(q)
		body=''
		if urllib2.urlopen(url).read() == 'OK':
			body='<table style="width:636px"><tbody><tr>'
			body+='<td class="title challengePopup2">'+GlobalTools.convertHTMLEntities(rt).encode('utf-8')+'</th>'
			body+='<td class="garbage challengePopup2">&gt;&gt;</th>'
			body+='<td class="name challengePopup2">'+q['name_to']+'</th>'
			body+='</tr></tbody></table>'
		else: body='<div class="tiny-title">Failed to load data.</div>'
	except Exception as e: body='<div class="tiny-title">Failed to load data.</div>'
	return body

def deleteChallenge(hash,id,direction):
	url='https://www.csie.ntu.edu.tw/~b00902017/LR2RR/delete.php?'
	try:
		q={}
		q['hash']=hash
		q['id2']=id
		q['direction']=direction
		with GlobalTools.dbLock:
			GlobalTools.cur.execute('''
				SELECT id
				FROM rivals
				WHERE active=2
			''')
			qq=GlobalTools.cur.fetchall()[0]
			q['id1']=qq['id']
		url+=urllib.urlencode(q)
		body=''
		if urllib2.urlopen(url).read() == 'OK':
			body='<div class="tiny-title">Deleted successfully.</div>'
		else: body='<div class="tiny-title">Failed to load data.</div>'
	except Exception as e: body='<div class="tiny-title">Failed to load data.</div>'
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
	with GlobalTools.dbLock:
		GlobalTools.cur.execute('''
			SELECT id
			FROM rivals
			WHERE active=2
		''')
		qq=GlobalTools.cur.fetchall()
		if len(qq)==0: return '<div class="small-title">No challenge records.</div>'
		url+='id='+str(qq[0]['id'])
	try:
		datas=json.loads(urllib2.urlopen(url).read())
		divs=[]
		for data in list(reversed(datas)):
			rr=generateOneQueryRow(data)
			div='<div class="ch-box'+rr['direction_class']+'">'
			div+='<div class="ch-component title"><a target="_blank" href="http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=ranking&amp;bmsmd5='+data['hash']+'">'+rr['title']+'</a></div>'
			div+='<div class="ch-component namelabel">&nbsp;'+rr['direction']+':</div>'
			div+='<div class="ch-component name"><a target="_blank" href="http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=mypage&playerid='+rr['id']+'">'+rr['name']+'</a></div>'
			div+='<div class="ch-component clear'+rr['clear_class']+'">'+rr['clear']+'</div>'
			div+='<div class="ch-component bp'+rr['bp_class']+'">'+rr['bp']+' BP</div>'
			div+='<div class="ch-component score"><div class="'+rr['score_class']+'" style="width:'+rr['score_rate']+'">&nbsp;'+rr['score_rate']+rr['score']+'</div></div>'
			div+='<div class="ch-component time">'+rr['time']+'</div>'
			div+='<div class="ch-component delete" hash="'+data['hash']+'" rid="'+rr['id']+'" direction="'+rr['direction']+'">Delete</div>'
			div+='<div class="ch-component more" hash="'+data['hash']+'">More</div>'
			div+='<div class="ch-component line'+rr['direction_class']+'"></div>'
			div+='</div>'
			divs+=div
		divs=''.join(divs)
		if len(datas)==0 :divs='<div class="small-title">No challenge records.</div>'
	except Exception as e: divs='<div class="small-title">Failed to load data.</div>'
	return divs.encode('utf-8')

def handleChallengeRequest(q_dict):
	res=GlobalTools.SimpleHTTPResponse()
	body=''
	if 'type' in q_dict:
		type=q_dict['type']
		if type=='add' and 'hash' in q_dict and 'id' in q_dict and 'name' in q_dict:
			body=addChallenge(q_dict['hash'],q_dict['id'],q_dict['name'])
		elif type=='delete' and 'hash' in q_dict and 'id' in q_dict and 'direction' in q_dict:
			body=deleteChallenge(q_dict['hash'],q_dict['id'],q_dict['direction'])
		elif type=='query':
			body=queryChallenge()
	return res,body