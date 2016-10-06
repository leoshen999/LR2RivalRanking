$(document).ready(function(){
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
	$("#myTable").tablesorter({
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
	$("#loading").hide();
	$("#loaded").show();
});


function resetFilterResult(){
	$(".song-tr").prop('hidden',false);
	
	var min_lv = $('.min-lv').prop('selectedIndex');
	var max_lv = $('.max-lv').prop('selectedIndex');
	$(".song-tr").each(function() {
		var lv = parseInt($(this).attr('hidden-level'));
		if( lv < min_lv || lv > max_lv) {
			$(this).closest("tr").prop('hidden',true);
		}
	});
	
	$('.ck-RANK input:checkbox:not(:checked)').each(function() {
		var rank = $(this).attr('value');
		$(".player.td-".concat(rank)).closest("tr").prop('hidden',true);
	});
	
	$('.ck-CLEAR input:checkbox:not(:checked)').each(function() {
		var clear = $(this).attr('value');
		$(".player.td-lamp.td-".concat(clear)).closest("tr").prop('hidden',true);
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
				data: {"hash":hash,"level":level,"title":title}
			})
			.done(function(data){
				$('.popup-content').html(data);
				setPopupPositionAndHeight();
			})
			.fail(function(){
					$('.popup-content').html('Failed to load data.');
			})
		;
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
					data: {"hash":hash,"level":level,"title":title}
				})
				.done(function(data){
					$('.popup-content').html(data);
					setPopupPositionAndHeight();
				})
				.fail(function(){
						$('.popup-content').html('Failed to load data.');
				})
			;
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