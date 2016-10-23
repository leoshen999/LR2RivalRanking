#coding: utf-8
import GlobalTools
import DPISocket
import WebpageExtensionHandler


def handleChallengePage(headers):
	sock=DPISocket.DPISocket('GET','/~lavalse/LR2IR/search.cgi?mode=detail')
	sock.setMsg(headers)
	res,body=sock.sendAndReceive()
	
	pre_def='''
		<script src="https://code.jquery.com/jquery-3.1.1.min.js"></script>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.27.8/js/jquery.tablesorter.min.js"></script>
		<style>'''+GlobalTools.webstyle+'''</style>
	'''
	title=u'<div class="big-title">挑戦状</div>'
	loading='<div class="small-title" id="loading">Loading...</div>'
	loaded='<div id="loaded" style="display: none"><div id="all-ch-box"></div><div class="popup"><div class="ESC-button">[ESC] Close</div><div class="popup-title1 small-title"></div><div class="popup-title2 small-title"></div><div class="popup-content"></div></div><div class="popup2"></div></div>'
	post_def='<script>var mode="challenge";'+GlobalTools.webscript+'</script>'
	
	newContents='<div id="myextend">'+pre_def+title+loading+loaded+post_def+'</div>'
	body=WebpageExtensionHandler.modifyContents(body,True,True,newContents)
	return res,body