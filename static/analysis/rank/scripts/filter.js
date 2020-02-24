var all = [];
var _priorities = [];
//console.log(_priorities);
var found = {
	"slot_1": [],
	"slot_2": [],
	"slot_3": [],
	"slot_4": [],
	"slot_5": [],
	"slot_6": [],
};
var json;
var raw = JSON.parse(window.data);
var _col = JSON.parse(window.col);	

$(document).ready(function() {
	
	//console.log(ts)
	var data = raw
	var w = 0;
	var h = 0.5;
	var height = 25;
	var sideWidth = screen.width - $("#bank").width() + 10;
	//console.log(_col);
	for (i = 0; i < _col.length; i++, w++) {
		
		$("#bank").append("<div class='tile' id='tile_"+i+"'>"+_col[i]+"</div>");
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
			if (result.length > 1) {
				result = result[1];
			}
			//console.log(found["slot_"+result]);
			console.log(result);
			found["slot_"+result].push($(el).text());
				//console.log(priorities['slot_'+i]);
		}
    }
	
function getData(handleData) {
	$.ajax({
		url:"post_filter",  
		success:function(ts) {
		data = JSON.parsets;
		console.log(data)
		}
	});
}

function handleData(data) {
	console.log(data);
}

function checkSlot() {
	_priorities.length = 0;
	found["slot_1"].length = 0;
	found["slot_2"].length = 0;
	found["slot_3"].length = 0;
	found["slot_4"].length = 0;
	found["slot_5"].length = 0;
	found["slot_6"].length = 0;
	for (i = 0; i < all.length; i++) {
		//console.log(priorities[key].length);
		gatherSlot(all[i]);
	}
	for (slot in found) {
		if (found[slot].length != 0) {
			_priorities.push(found[slot][0]);
		} 
	}
	$.ajax({
		method: "POST",
		url: "post_filter",
		data: {'data': JSON.stringify(_priorities)}
	});
	console.log(_priorities);
	//var text = readTextFile("file:///C:/Users/noahs/Desktop/ghscouting/json.txt");
	//console.log(text);
	//console.log(gatherData(raw, priorities));
}