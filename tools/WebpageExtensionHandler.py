#coding: utf-8
import lxml.html

import GlobalTools

def modifyContents(body,appendMenu=True,changeContent=False,newContent=''):
	body=body.decode('cp932')
	try:
		if appendMenu is True:
			appM=u' | <a href="search.cgi?mode=recent">最近の遊び記録</a><br>難易度表： '
			cnt=0
			ll=len(GlobalTools.table_info)
			for table,info in GlobalTools.table_info.iteritems():
				appM+=u'<a href="search.cgi?mode=difficulty&table='+table+'">'+info[0]+'</a>'
				cnt+=1
				if cnt<ll: appM+=' | '
			
			pos=body.find('</div><!--end menu-->')
			body=body[:pos]+appM+body[pos:]
		
		if changeContent is True:
			st=body.find('<div id="search">')
			en=body.find('<div id="foot">')
			body=body[:st]+newContent+body[en:]
	except Exception as e:
		print e
	
	return body.encode('cp932','ignore')
