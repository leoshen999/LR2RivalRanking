#coding: utf-8
from urlparse import urljoin
import lxml.html
import sqlite3
import urllib2
import json
import io

import GlobalTools
import DPISocket
import DifficultyGenerator


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
			for name,info in table_info.iteritems():
				message=' Update '+info[0]+'...'
				margin=' ' * (34-GlobalTools.strWidth(message))
				GlobalTools.logger.write(message+margin+'\n')
				
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
				
				with io.open(GlobalTools.dbdir+name+'_body.json', 'w', encoding='utf-8') as fp:
					fp.write(unicode(json.dumps(songs, ensure_ascii=False, encoding="utf-8")))
					# json.dump(songs,fp,ensure_ascii=False)
				with io.open(GlobalTools.dbdir+name+'_level_order.json', 'w', encoding='utf-8') as fp:
					fp.write(unicode(json.dumps(level_order, ensure_ascii=False, encoding="utf-8")))
					# json.dump(level_order,fp,ensure_ascii=False)
			GlobalTools.misc['webpageextension']='True'
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
		menu.append(lxml.html.fromstring(u'<div>難易度表： <a href="search.cgi?difficultytable=normal">☆通常難易度表</a> | <a href="search.cgi?difficultytable=insane">★発狂BMS難易度表</a> | <a href="search.cgi?difficultytable=normal_no2">▽第2通常難易度</a> | <a href="search.cgi?difficultytable=insane_no2">▼第2発狂難易度</a> | <a href="search.cgi?difficultytable=ln">◆LN難易度</a> | <a href="search.cgi?difficultytable=overjoy">★★Overjoy</a></div>'))
	
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
	body=lxml.html.tostring(root,encoding='cp932')
	return body

def handleDifficultyTableSearch(headers,q_dict):
	sock=DPISocket.DPISocket('GET','/~lavalse/LR2IR/search.cgi?mode=detail')
	sock.setMsg(headers)
	res,body=sock.sendAndReceive()
	
	table='normal_no2'
	if q_dict['difficultytable'][0] in table_info :
		table = q_dict['difficultytable'][0]
	
	newContents='<br><h1>'+table_info[table][0]+'</h1><h2 id="loading">Loading...</h2>'
	
	newContents+=DifficultyGenerator.difficultyGenerator.generateDifficulty(table)
	
	body='<!DOCTYPE html>\n'+modifyContents(body,True,True,newContents)
	
	return res,body

def handleDifficultyTableHashSearch(q_dict):
	
	res=GlobalTools.SimpleHTTPResponse()
	level=q_dict['level'][0]
	title=q_dict['title'][0]
	hash=q_dict['difficultytablehash'][0]
	body=DifficultyGenerator.difficultyGenerator.generatePopup(level,title,hash).encode('utf8')
	return res,body















