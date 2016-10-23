#coding: utf-8
import lxml.html

import GlobalTools

def modifyContents(body,appendMenu=True,changeContent=False,newContent=''):
	
	try:
		root=lxml.html.fromstring(body)
		menu=root.find('.//div[@id="menu"]')
		
		if appendMenu is True:
			menu.getchildren()[-1].tail=' | '
			menu.append(lxml.html.fromstring(u'<a href="search.cgi?mode=challenge">挑戦状</a>'))
			menu.getchildren()[-1].tail=' | '
			menu.append(lxml.html.fromstring(u'<a href="search.cgi?mode=recent">最近の遊び記録</a>'))
			menu.append(lxml.html.fromstring(u'<br>'))
			menu.getchildren()[-1].tail=u'難易度表： '
			cnt=0
			for table,info in GlobalTools.table_info.iteritems():
				menu.append(lxml.html.fromstring(u'<a href="search.cgi?mode=difficulty&table='+table+'">'+info[0]+'</a>'))
				cnt+=1
				if cnt<6: menu.getchildren()[-1].tail=' | '
		
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
	except Exception as e: pass
	
	return body
