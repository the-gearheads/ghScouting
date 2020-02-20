var all = [];
var _priorities = [];

var found = {};

var dataPoints = [];

var raw = JSON.parse(window.data);
var _col = JSON.parse(window.col);

$(document).ready(function() {
	
	var data = raw
	var w = 0;
	var h = 0;
	var height = 25;
	var sideWidth = screen.width - $("#bank").width() + 10;
	//console.log(_col);
	for (i = 0; i < _col.length; i++, w++) {
		$("#bank").append("<div class='tile' id='tile_"+i+"'><p>"+_col[i]+"</p></div>");
		var div = '#tile_'+i;
		//console.log(div.width);
		var threshold = i/16;
		if (Number.isInteger(threshold) && i != 0) {
			height = $(div).height();
			w = 0
			h = h + 1;
			$(div).offset({top: height * h, left: sideWidth + 0});
		} else {
			$(div).offset({top: height * h, left:  sideWidth + $(div).width() * w});
		}
		all.push($("#tile_"+i));
		
	}

	$( ".tile" ).draggable({
		containment: "#sweetmotherofpearl", 
		scroll: false,
		snap: ".slot",
		snapMode: "inner"
	});
	
	$( "#sweetmotherofpearl" ).droppable({
		drop: function( event, ui ) {
			//Get the position before changing the DOM
			var p1 = ui.draggable.parent().offset();
			//Move to the new parent
			$(this).append(ui.draggable);
			//Get the postion after changing the DOM
			var p2 = ui.draggable.parent().offset();
			//Set the position relative to the change
			ui.draggable.css({
			  top: parseInt(ui.draggable.css('top')) + (p1.top - p2.top),
			  left: parseInt(ui.draggable.css('left')) + (p1.left - p2.left)
			});
		}
	});	
});

function gatherData(array, array2) {//, array2, obj) {
	for (team in array) {
		var properties = _col;
		var value = Object.values(array[team]);
		var largeObj =  {};
		//console.log(array[team]);
		
		for (var member in array[team]) delete array[team][member];
		largeObj.team = array[team];
		//console.log(largeObj);
		for (item in array2) {
			array[team] = array2[item];
		}
	}
	//console.log(largeObj);
	//console.log(name);
}

function gatherSlot(el) { 
		var snapped = $(el).data('uiDraggable').snapElements;
       
        /* Pull out only the snap targets that are "snapping": */
        var snappedTo = $.map(snapped, function(element) {
            return element.snapping ? element.item : null;
        });
       
        /* Display the results: */
        var result= '';
        $.each(snappedTo, function(idx, item) {
            result += $(item).text() + "";
        });
        if (result != '') {
			_priorities.splice(result, 0, $(el).text());
				//console.log(priorities['slot_'+i]);
		}
    }
	/*var snapped = $(element).data('uiDraggable').snapElements;
       
	var snappedTo = $.map(snapped, function(element) {
		return element.snapping ? element.item : null;
	});
       
	/* Display the results: 
	var result= '';
	$.each(snappedTo, function(idx, item) {
		result += $(item).text() + "";
	});
	//console.log(result);
	//console.log(result);
	if (result != "") {
		priorities["slot_"+result].push(element);
		//_priorities.push(element[0].innerHTML);
		var length = priorities["slot_"+result].length;
		for (y = 0; y < length - 1; y++) {
			priorities["slot_"+result].pop();
		}
		console.log(priorities["slot_"+i].length);
		for (i = 1; i <= 6; i++) {
			if (priorities["slot_"+i].length == 0) {
				console.log("bruh");
			}
		}
			
				
	} else {
		return null;
	}
	
}*/

function checkSlot() {
	_priorities.length = 0;
	for (i = 0; i < all.length; i++) {
		//console.log(priorities[key].length);
		gatherSlot(all[i]);
	}
	$.ajax({
		method: "POST",
		url: "post_filter",
		data: {'data': JSON.stringify(_priorities)}
	});
	console.log(_priorities)
	//console.log(gatherData(raw, priorities));
}