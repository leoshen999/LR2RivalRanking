$(document).ready(function(){
	$.tablesorter.addParser({
		id: 'Level',
		is: function(s) {
			return false;
		},
		format: function(s) {
			return level_order.indexOf(s);
		},
		type: 'numeric'
	});
	$("#myTable").tablesorter({
		headers: { 
			0: {sorter:'Level'}
		},
		textSorter: {
			1: $.tablesorter.sortText
		},
		sortAppend: [[0,0],[1,0]],
		sortList: [[0,0],[1,0]]
	}); 
	
	$("#myTable").tablesorter();
	$("#loading").hide();
	$("#loaded").show();
});


function resetFilterResult(){
	$(".song-tr").show();

	var min_lv = $('.min-lv').prop('selectedIndex');
	var max_lv = $('.max-lv').prop('selectedIndex');
	$(".song-tr").each(function() {
		var lv = parseInt($(this).attr('hidden-level'));
		if( lv < min_lv || lv > max_lv) {
			$(this).closest("tr").hide();
		}
	});
	
	$('.RANK:checkbox:not(:checked)').each(function() {
		var rank = $(this).attr('value');
		if(rank === "C-F"){
			$(".player.td-CF").closest("tr").hide();
		} else{
			$(".player.td-".concat(rank)).closest("tr").hide();
		}
	});

	$('.CLEAR:checkbox:not(:checked)').each(function() {
		var clear = $(this).attr('value');
		if(clear === "FULLCOMBO")$(".player.td-FC").closest("tr").hide();
		else if(clear === "HARD")$(".player.td-HC").closest("tr").hide();
		else if(clear === "NORMAL")$(".player.td-CL").closest("tr").hide();
		else if(clear === "EASY")$(".player.td-EC").closest("tr").hide();
		else if(clear === "FAILED")$(".player.td-FA").closest("tr").hide();
		else if(clear === "NOPLAY")$(".player.td-NO").closest("tr").hide();
	});

}

function setPopupPositionAndHeight(){
	$('.popup').height('auto');
	var h=$('.popup')[0].scrollHeight+2;
	var window_h=$(window).height();
	var min_h=Math.min(h,window_h);
	
	$('.popup').outerHeight(min_h);
	$('.popup').css('margin-top','-'+(min_h/2)+'px');
}


var toggled=false;
var toggledHash='';
$('.td-playedN').mouseenter(function(){
	if(!toggled){
		var hash = $(this).attr('hash');
		var level=$(this).siblings('.td-level').text();
		var title=$(this).siblings('.td-title').children('a').text();
		
		$('.popup-content').html('Loading...');
		setPopupPositionAndHeight();
		
		$('.popup').css('visibility', 'visible');
		$.ajax({
			url: '/~lavalse/LR2IR/search2.cgi',
			type: "get",
			data: {"difficultytablehash":hash,"level":level,"title":title},
			success: function(data){
				$('.popup-content').html(data);
				setPopupPositionAndHeight();
		}});
	}
});
$('.td-playedN').mouseleave(function(){
	if (!toggled)
		$('.popup').css('visibility', 'hidden');
});

$('.td-playedN').click(function(){
	var hash=$(this).attr('hash');
	if(!toggled){
		$(this).addClass('td-toggled');
		toggledHash=hash;
		toggled=true;
	}
	else{
		if(toggledHash===hash){
			$(this).removeClass('td-toggled');
			toggled=false;
		}
		else{
			$('.td-playedN[hash="'+toggledHash+'"]').removeClass('td-toggled');
			$(this).addClass('td-toggled');
			toggledHash=hash;
			
			var level=$(this).siblings('.td-level').text();
			var title=$(this).siblings('.td-title').children('a').text();
			
			$('.popup-content').html('Loading...');
			setPopupPositionAndHeight();
			
			$.ajax({
				url: '/~lavalse/LR2IR/search2.cgi',
				type: "get",
				data: {"difficultytablehash":hash,"level":level,"title":title},
				success: function(data){
					$('.popup-content').html(data);
					setPopupPositionAndHeight();
			}});
		}
	}
});
$(document).keyup(function(e) {
	if (toggled && e.keyCode === 27){
		$('.td-playedN[hash="'+toggledHash+'"]').removeClass('td-toggled');
		toggled=false;
		$('.popup').css('visibility', 'hidden');
	}
});

$('.ESC-button').click(function(){
	if (toggled){
		$('.td-playedN[hash="'+toggledHash+'"]').removeClass('td-toggled');
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