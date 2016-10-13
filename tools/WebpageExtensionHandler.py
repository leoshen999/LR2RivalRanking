#coding: utf-8
from urlparse import urljoin
import lxml.html
import sqlite3
import urllib2
import json

import GlobalTools
import DPISocket
import DifficultyGenerator
import ChallengeGenerator


table_info={
	'normal_no2':[u'▽第2通常難易度','http://bmsnormal2.syuriken.jp/table.html'],
	'insane_no2':[u'▼第2発狂難易度','http://bmsnormal2.syuriken.jp/table_insane.html'],
	'normal':[u'☆通常難易度表','http://www.ribbit.xyz/bms/tables/normal.html'],
	'insane':[u'★発狂BMS難易度表','http://www.ribbit.xyz/bms/tables/insane.html'],
	'overjoy':[u'★★Overjoy','http://www.ribbit.xyz/bms/tables/overjoy.html'],
	'ln':[u'◆LN難易度','http://flowermaster.web.fc2.com/lrnanido/gla/LN.html']
}

def handleWebpageExtensionSetup(flag):
	with GlobalTools.lock:
		GlobalTools.logger.write( '---- Setup webpage extension -----\n' )
		
		if flag:
			GlobalTools.logger.write( ' Update:                          \n' )
			cnt=0
			for name,info in table_info.iteritems():
				cnt+=1
				cntMessage='%d/%d'%(cnt,6)
				margin=' ' * (26-len(cntMessage))
				cntMessage='<font\tstyle="color:LightGray">%d</font>/%d'%(cnt,6)
				GlobalTools.logger.writeCurrentLine( ' Update:'+margin+cntMessage+'\n' )
				
				web_url=info[1]
				web_src=urllib2.urlopen(web_url).read()
				
				header_url=urljoin(web_url,lxml.html.fromstring(web_src).find('.//meta[@name="bmstable"]').attrib['content'])
				header_src=urllib2.urlopen(header_url).read()
				header=json.loads(header_src)
				
				body_url=urljoin(header_url,header['data_url'])
				body_src=urllib2.urlopen(body_url).read()
				body=json.loads(body_src)
				
				if 'level_order' not in header:
					tempLv={}
					for song in body:
						if song['level'].isdigit(): tempLv[song['level']]=int(song['level'])
						else: tempLv[song['level']]=99999999
					header['level_order']=sorted(tempLv, key=tempLv.get)
				for idx in range(len(header['level_order'])):
					if isinstance(header['level_order'][idx],int):
						header['level_order'][idx]=str(header['level_order'][idx])
				
				songs={}
				level_order=[]
				for song in body:
					songs[ unicode(song['md5']) ] = [ unicode(song['level']) , unicode(song['title']) ]
				for level in header['level_order']:
					level_order.append(unicode(level))
				
				with open(GlobalTools.dbdir+name+'_body.json', 'w') as fp:
					fp.write(json.dumps(songs, ensure_ascii=False, encoding="utf-8").encode('utf-8'))
				with open(GlobalTools.dbdir+name+'_level_order.json', 'w') as fp:
					fp.write(json.dumps(level_order, ensure_ascii=False, encoding="utf-8").encode('utf-8'))
			GlobalTools.misc['webpageextension']='True'
			GlobalTools.logger.write( ' Difficulty table links:          \n' )
			for name,info in table_info.iteritems():
				width=GlobalTools.strWidth(info[0])
				link='<a\thref="http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?difficultytable='+name+'"\tstyle="color:LightGray;text-decoration:none">'+info[0]+'</a>'
				margin=' '*(34-width)
				GlobalTools.logger.write( margin+link+'\n' )
		else:
			GlobalTools.logger.write( '    Disable webpage extension     \n' )
			GlobalTools.misc['webpageextension']='False'
		conn = sqlite3.connect(GlobalTools.dbpath)
		conn.row_factory = sqlite3.Row
		cur = conn.cursor()
		try:
			cur.execute('''
				REPLACE INTO misc VALUES('webpageextension',?)
			''',(GlobalTools.misc['webpageextension'],))
			conn.commit()
		except sqlite3.Error as er:
			conn.rollback()
			conn.close()
			GlobalTools.logger.write( '     Failed to save settings      \n' )
			GlobalTools.logger.write( '----------------------------------\n' )
			GlobalTools.logger.write( '\n' )
			return
		conn.close()
		GlobalTools.logger.write( '----------------------------------\n' )
		GlobalTools.logger.write( '\n' )

def modifyContents(body,appendMenu=True,changeContent=False,newContent=''):
	
	root=lxml.html.fromstring(body)
	menu=root.find('.//div[@id="menu"]')
	
	if appendMenu is True:
		menu.getchildren()[-1].tail=' | '
		menu.append(lxml.html.fromstring(u'<a href="search.cgi?mode=challenge">挑戦状</a>'))
		menu.getchildren()[-1].tail=' | '
		menu.append(lxml.html.fromstring(u'<a href="search.cgi?mode=recent">最近の遊び記録</a>'))
		menu.append(lxml.html.fromstring(u'<div>難易度表： <a href="search.cgi?mode=difficulty&table=normal">☆通常難易度表</a> | <a href="search.cgi?mode=difficulty&table=insane">★発狂BMS難易度表</a> | <a href="search.cgi?mode=difficulty&table=normal_no2">▽第2通常難易度</a> | <a href="search.cgi?mode=difficulty&table=insane_no2">▼第2発狂難易度</a> | <a href="search.cgi?mode=difficulty&table=ln">◆LN難易度</a> | <a href="search.cgi?mode=difficulty&table=overjoy">★★Overjoy</a></div>'))
	
	if changeContent is True:
		parent=menu.getparent()
		idx=parent.index(menu)+1
		while True:
			elem=parent[idx]
			if elem.tag=='div' and 'id' in elem.attrib and elem.attrib['id']=='foot':
				parent.insert(idx,lxml.html.fromstring(newContent))
				break
			else:
				parent.remove(elem)
	body='<!DOCTYPE html>\n'+lxml.html.tostring(root,encoding='cp932')
	return body

def handleDifficultyTableSearch(headers,q_dict):
	sock=DPISocket.DPISocket('GET','/~lavalse/LR2IR/search.cgi?mode=detail')
	sock.setMsg(headers)
	res,body=sock.sendAndReceive()
	
	table='normal_no2'
	if q_dict['table'][0] in table_info :
		table = q_dict['table'][0]
	
	pre_def='''
		<script src="https://code.jquery.com/jquery-3.1.1.min.js"></script>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.27.8/js/jquery.tablesorter.min.js"></script>
		<style>'''+GlobalTools.webstyle+'''</style>
	'''
	post_def='<script>'+GlobalTools.webscript+'</script>'
	
	newContents='<div id="myextend">'+pre_def+'<div class="big-title">'+table_info[table][0]+'</div>'+DifficultyGenerator.difficultyGenerator.generateDifficulty(table)+post_def+'</div>'
	
	body=modifyContents(body,True,True,newContents)
	
	return res,body

def handleDifficultyTableHashSearch(q_dict):
	
	res=GlobalTools.SimpleHTTPResponse()
	level=''
	if 'level' in q_dict: level=q_dict['level'][0]+'<br>'
	title=q_dict['title'][0]
	hash=q_dict['hash'][0]
	body=DifficultyGenerator.difficultyGenerator.generatePopup(level,title,hash).encode('utf8')
	return res,body

def handleChallenge(headers):
	sock=DPISocket.DPISocket('GET','/~lavalse/LR2IR/search.cgi?mode=detail')
	sock.setMsg(headers)
	res,body=sock.sendAndReceive()
	
	pre_def='''
		<script src="https://code.jquery.com/jquery-3.1.1.min.js"></script>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.27.8/js/jquery.tablesorter.min.js"></script>
		<style>'''+GlobalTools.webstyle+'''</style>
	'''
	post_def='<script>var mode="challenge";'+GlobalTools.webscript+'</script>'
	
	loading='<div class="small-title" id="loading">Loading...</div>'
	popup='<div class="popup"><div class="ESC-button">[ESC] Close</div><div class="popup-content"></div></div>'
	popup2='<div class="popup2"></div>'
	loaded='<div id="loaded" style="display: none"><div id="all-ch-box"></div>'+popup+popup2+'</div>'
	
	newContents=u'<div id="myextend">'+pre_def+u'<div class="big-title">挑戦状</div>'+loading+loaded+post_def+'</div>'
	body=modifyContents(body,True,True,newContents)
	return res,body

def handleChallengeAddDeleteQuery(q_dict):
	type=q_dict['type'][0]
	res=GlobalTools.SimpleHTTPResponse()
	body=''
	if type=='add':
		body=ChallengeGenerator.addChallenge(q_dict['hash'][0],q_dict['id'][0],q_dict['name'][0])
	elif type=='delete':
		body=ChallengeGenerator.deleteChallenge(q_dict['hash'][0],q_dict['id'][0],q_dict['direction'][0])
	elif type=='query':
		body=ChallengeGenerator.queryChallenge()
	return res,body

def handleRecent(headers):
	sock=DPISocket.DPISocket('GET','/~lavalse/LR2IR/search.cgi?mode=detail')
	sock.setMsg(headers)
	res,body=sock.sendAndReceive()
	
	pre_def='''
		<script src="https://code.jquery.com/jquery-3.1.1.min.js"></script>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.27.8/js/jquery.tablesorter.min.js"></script>
		<style>'''+GlobalTools.webstyle+'''</style>
	'''
	post_def='<script>'+GlobalTools.webscript+'</script>'
	
	newContents='<div id="myextend">'+pre_def+u'<div class="big-title">最近の遊び記録</div>'+DifficultyGenerator.difficultyGenerator.generateRecent()+post_def+'</div>'
	
	body=modifyContents(body,True,True,newContents)
	
	return res,body








