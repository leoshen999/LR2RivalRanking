#coding: utf-8
from urlparse import urljoin
import lxml.html
import urllib2
import json
import datetime,time

import GlobalTools

def updateDifficulties():
	with GlobalTools.logLock:
		try:
			table_l=len(GlobalTools.table_info)
			cnt=0
			GlobalTools.logger.write( '<div class="one-row"><span class="title">Update difficulties progress: <span class="highlight">0 / '+str(table_l)+'</span></span></div>' )
			for table,info in GlobalTools.table_info.iteritems():
				cnt+=1
				GlobalTools.logger.write( '<div class="one-row"><span class="title">Update difficulties progress: <span class="highlight">'+str(cnt)+' / '+str(table_l)+'</span></span></div>',False )
				
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
				
				with open(GlobalTools.dbdir+table+'_body.json', 'w') as fp:
					fp.write(json.dumps(songs, ensure_ascii=False, encoding="utf-8").encode('utf-8'))
				with open(GlobalTools.dbdir+table+'_level_order.json', 'w') as fp:
					fp.write(json.dumps(level_order, ensure_ascii=False, encoding="utf-8").encode('utf-8'))
			with GlobalTools.dbLock:
				GlobalTools.misc['difficultieslastupdate']=datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')
				GlobalTools.cur.execute('REPLACE INTO misc VALUES("difficultieslastupdate",?)',(GlobalTools.misc['difficultieslastupdate'],))
				GlobalTools.logger.writeDifficultiesLastupdate(GlobalTools.misc['difficultieslastupdate'])
				GlobalTools.conn.commit()
			for table,info in GlobalTools.table_info.iteritems():
				GlobalTools.logger.write( '<div class="one-row"><span class="title"><a target="_blank" href="http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=difficulty&amp;table='+table+'">'+info[0]+'</a></span></div>' )
		except Exception as e:
			GlobalTools.conn.rollback()
			GlobalTools.logger.write('<div class="one-row"><span class="title">Failed to update difficulties.</span></div>')
		GlobalTools.logger.write('<div class="one-row"><hr></div>')