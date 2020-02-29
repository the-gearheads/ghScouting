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
var data;
var raw = JSON.parse(window.data);
var _col = JSON.parse(window.col);	
var newCol = JSON.parse(window.newCol);
console.log(newCol);
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

function removeDuplicates(array) {
  return array.filter((a, b) => array.indexOf(a) === b)
};

function setParent(el, newParent) {
	newParent.appendChild(el);
}

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

function getKeyByValue(object, value) {
	return Object.keys(object).find(key => object[key] === value);
	
	/*for (key in object) {
		console.log(key, object[key], value)
		if (object[key] == value) {
			return key;
		}
	}*/
}

function createContent(key) {
	var string;
	var attr = [];
	for (team in raw) {
		if (team == key) {
			//var names = Object.keys(raw[team]);
			var values = Object.values(raw[team]);
			var valueArr = removeDuplicates(newCol);
			//console.log(names.length, values);
			for (i = 0; i < values.length; i++) {
				var div =  "#list_tile_"+key;
				//console.log(names[i], i);
				var name = valueArr[i];
				attr.push('<i>'+name+'</i>'+ ': ' + "<font color = 'red'>"+values[i]+"</font>");
				string = attr.join('<br/>');
				
			}
			$(div).append("<div class='content'>"+string+"</div>");
		}
	}
}

function Populate(data) {
	//console.log("wack");
	$("#list").empty()
	var w = 0;
	var y = 1;
	var width = screen.width - $("#list").width() + 10;
	var height = 250;
	let array = Object.values(data);
	//console.log(array.length);
	for (i = 0; i < array.length + 1; i++, w++) {
		var max = Math.max(...array);
		var key = getKeyByValue(data, max);
		//console.log(key, max);
		if (key == null) {
			//console.log("true");
			var key = Object.keys(data)[0];
			var max = Object.values(data)[0];
			//console.log(key, max)
		}
		//console.log(key);
		$("#list").append("<div class='list_tile' id='list_tile_"+key+"'>"+ key + ': ' + max+"</div>");
		var div =  "#list_tile_"+key;
		$(div).append("<button type='button' onclick='go("+key+")' class='list_button'>+</button>");
		//$(div).append("<div class='content'></div>");
		
		
		
		if (Number.isInteger(w/6) && w != 0) {
			w = 0;
			height = 250;
			width = width + $(div).width() + 10;
			$(div).offset({top: height + 50 + 10, left: width});
		} else {
			height =  height + $(div).height() + 10;			
			$(div).offset({top: height, left: width});
		}
		
		data = _.omit(data, key);
		array.splice(array.indexOf(max), 1);
		i = 0;
		
		
		//console.log(data);
	}
	
	//console.log(max);
	/*for (team in data) {
		//console.log(data[team], array[0])
		for (item in array) {
			if (data[team] == array[item]) {
				w = array.indexOf(array[item]);
				
			}
		}
	
		$("#list").append("<div class='list_tile' id='list_tile_"+team+"'><p>"+ team + ': ' + data[team]+"</p></div>");
		var div = "#list_tile_"+team;
		console.log(w);
		$(div).offset({top: $(div).height() * w, left: 10});
	}*/
}
	
	/*for (team in data) {
		score = data[team];
		
		//$("#list").append("<div class='list_tile'><p>"+ team + ': ' + score+"</p></div>");
	}*/


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
		data: {'data': JSON.stringify(_priorities)},
		success: function(data) {
			data = JSON.parse(data);
			console.log(data);
			Populate(data);
		}
	});
	console.log(_priorities);
	//var text = readTextFile("file:///C:/Users/noahs/Desktop/ghscouting/json.txt");
	//console.log(text);
	//console.log(gatherData(raw, priorities));
}

function go(key) {
	$("#content_corner").empty();
	var div = "#list_tile_"+key;
	//console.log($(div)[0]);
	createContent(key);
	$(div)[0].childNodes[2].style.display = "inline-block";
	//$(div)[0].childNodes[2].style.position = "absolute";
	setParent($(div)[0].childNodes[2], $("#content_corner")[0]);
	
	//$($(div)[0].childNodes[2]).position() ==  $("#content_corner").position();
	//console.log($($(div)[0].childNodes[2]).position());
	/*$($(div)[0].childNodes[2]).position({
		of: $("#content_corner")
	});*/
	
}