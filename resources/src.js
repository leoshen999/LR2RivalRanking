$(document).ready(function(){
	if(mode==='difficulty'){
		$.tablesorter.addParser({
			id: 'level',
			is: function(s) {return false;},
			format: function(s) {
				return level_order.indexOf(s);
			},
			type: 'numeric'
		});
		$.tablesorter.addParser({
			id: 'playedN',
			is: function(s) {return false;},
			format: function(s){
				return s.replace(/^-$/,'');
			},
			type: 'numeric'
		});
		$("#playerTable").tablesorter({
			headers: { 
				0: {sorter:'level'},
				6: {sorter:'playedN'}
			},
			textSorter: {
				1: $.tablesorter.sortText
			},
			sortAppend: [[0,0],[1,0]],
			sortList: [[0,0],[1,0]]
		}); 
		
		$("#myTable").tablesorter();
		setPopupEvent();
		$("#loading").hide();
		$("#loaded").show();
		resetFilterResult();
	}
	if(mode==='recent'){
		setPopupEvent();
		$("#loading").hide();
		$("#loaded").show();
	}
});


function resetFilterResult(){
	var min_lv = $('.min-lv').prop('selectedIndex');
	var max_lv = $('.max-lv').prop('selectedIndex');
	$(".song-tr").each(function() {
		var lv = parseInt($(this).attr('hidden-level'));
		if( lv < min_lv || lv > max_lv)
			$(this).prop('hidden',true);
		else $(this).prop('hidden',false);
	});
	
	$('.ck input:checkbox:not(:checked)').each(function() {
		var unchecked = $(this).attr('value');
		$('.song-tr.'+unchecked).prop('hidden',true);
	});
	
	$('.ck-status.MAX').html($('.song-tr.MAX:visible').length);
	$('.ck-status.AAA').html($('.song-tr.AAA:visible').length);
	$('.ck-status.AA').html($('.song-tr.AA:visible').length);
	$('.ck-status.A').html($('.song-tr.A:visible').length);
	$('.ck-status.BF').html($('.song-tr.BF:visible').length);
	
	$('.ck-status.FC').html($('.song-tr.FC:visible').length);
	$('.ck-status.HC').html($('.song-tr.HC:visible').length);
	$('.ck-status.CL').html($('.song-tr.CL:visible').length);
	$('.ck-status.EC').html($('.song-tr.EC:visible').length);
	$('.ck-status.FA').html($('.song-tr.FA:visible').length);
	$('.ck-status.NO').html($('.song-tr.NO:visible').length);
	
	
}

var toggled=false;
var toggledHash='';

function setPopupPositionAndHeight(){
	$('.popup').height('auto');
	var h=$('.popup')[0].scrollHeight+2;
	var window_h=window.innerHeight;//$(window).height();
	if (window_h>50)window_h-=50;
	var min_h=Math.min(h,window_h);
	
	$('.popup').outerHeight(min_h);
	$('.popup').css('margin-top','-'+(min_h/2)+'px');
}
function setPopupContent(hash,level,title){
	$('.popup-title1').html(level);
	$('.popup-title2').html('<a target="_blank" href="http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=ranking&amp;bmsmd5='+hash+'">'+title+'</a>')
	$('.popup-content').html('<div class="small-title">Loading...</div>');
	setPopupPositionAndHeight();
	
	$('.popup').css('visibility', 'visible');
	$.ajax({
			url: '/~lavalse/LR2IR/ranking.cgi',
			type: "get",
			data: {"hash":hash}
		})
		.done(function(data){
			$('.popup-content').html(data);
			setPopupPositionAndHeight();
		})
		.fail(function(){
			$('.popup-content').html('<div class="small-title">Failed to load data.</div>');
			setPopupPositionAndHeight();
		})
	;
}

function setPopupEvent(){
	$('td.playedN').mouseenter(function(){
		if(!toggled){
			var hash = $(this).attr('hash');
			var level=$(this).siblings('.level, .line').text();
			var title=$(this).siblings('.title').children('a').text();
			
			setPopupContent(hash,level,title);
		}
	});
	$('td.playedN').mouseleave(function(){
		if (!toggled)
			$('.popup').css('visibility', 'hidden');
	});

	$('td.playedN').click(function(){
		var hash=$(this).attr('hash');
		if(!toggled){
			toggledHash=hash;
			toggled=true;
			$('td.playedN[hash="'+toggledHash+'"]').addClass('toggled');
		}
		else{
			if(toggledHash===hash){
				$('td.playedN[hash="'+toggledHash+'"]').removeClass('toggled');
				toggled=false;
			}
			else{
				$('td.playedN[hash="'+toggledHash+'"]').removeClass('toggled');
				toggledHash=hash;
				$('td.playedN[hash="'+toggledHash+'"]').addClass('toggled');
				
				var level=$(this).siblings('.level, .line').text();
				var title=$(this).siblings('.title').children('a').text();
				
				setPopupContent(hash,level,title);
			}
		}
	});
}



$(document).keyup(function(e) {
	if (toggled && e.keyCode === 27){
		$('td.playedN[hash="'+toggledHash+'"]').removeClass('toggled');
		toggled=false;
		$('.popup').css('visibility', 'hidden');
	}
});
$('.ESC-button').click(function(){
	if (toggled){
		$('td.playedN[hash="'+toggledHash+'"]').removeClass('toggled');
		toggled=false;
		$('.popup').css('visibility', 'hidden');
	}
});


var waitForFinalEvent = (function () {
	var timers = {};
	return function (callback, ms, uniqueId) {
		if (!uniqueId) {
			uniqueId = "Don't call this twice without a uniqueId";
		}
		if (timers[uniqueId]) {
			clearTimeout (timers[uniqueId]);
		}
		timers[uniqueId] = setTimeout(callback, ms);
	};
})();
$(window).resize(function () {
	waitForFinalEvent(function(){
		setPopupPositionAndHeight()
	}, 500, "unique-string");
});