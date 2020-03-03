var all = [];
var _priorities = {};
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
	
	var data = raw
	var w = 0;
	var h = 0.5;
	var height = 25;
	var sideWidth = screen.width - $("#bank").width() + 10;
	for (i = 0; i < _col.length; i++, w++) {
		
		$("#bank").append("<div class='tile' id='tile_"+i+"'>"+_col[i]+"<form><input type='number' id='input_"+i+"'></form></div>");
		var div = '#tile_'+i;
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

function getInput(el) {
	var usrInput = el[0].childNodes[1].childNodes[0].value;
	if (usrInput == "") {
		usrInput = 0;
	}
	return usrInput;
}

function gatherData(array, array2) {
	for (team in array) {
		var properties = _col;
		var value = Object.values(array[team]);
		var largeObj =  {};
		
		for (var member in array[team]) delete array[team][member];
		largeObj.team = array[team];
		for (item in array2) {
			array[team] = array2[item];
		}
	}
}

function gatherSlot(el) { 
		var snapped = $(el).data('uiDraggable').snapElements;
       
        var snappedTo = $.map(snapped, function(element) {
            return element.snapping ? element.item : null;
        });
       
        var result= '';
        $.each(snappedTo, function(idx, item) {
            result += $(item).text() + "";
        });
        if (result != '') {
			if (result.length > 1) {
				result = result[1];
			}
			console.log(result);
			found["slot_"+result].push($(el).text());
		}
}

function getKeyByValue(object, value) {
	return Object.keys(object).find(key => object[key] === value);
}

function createContent(key) {
	var string;
	var attr = [];
	for (team in raw) {
		if (team == key) {
			var values = Object.values(raw[team]);
			var valueArr = removeDuplicates(newCol);
			for (i = 0; i < values.length; i++) {
				var div =  "#list_tile_"+key;
				var name = valueArr[i];
				attr.push('<i>'+name+'</i>'+ ': ' + "<font color = 'red'>"+values[i]+"</font>");
				string = attr.join('<br/>');
				
			}
			$(div).append("<div class='content'>"+string+"</div>");
		}
	}
}

function Populate(data) {
	$("#list").empty()
	var w = 0;
	var y = 1;
	var width = screen.width - $("#list").width() + 10;
	var height = 250;
	let array = Object.values(data);
	for (i = 0; i < array.length + 1; i++, w++) {
		var max = Math.max(...array);
		var key = getKeyByValue(data, max);
		if (key == null) {
			var key = Object.keys(data)[0];
			var max = Object.values(data)[0];
		}
		$("#list").append("<div class='list_tile' id='list_tile_"+key+"'>"+ key + ': ' + max+"</div>");
		var div =  "#list_tile_"+key;
		$(div).append("<button type='button' onclick='go("+key+")' class='list_button'>+</button>");
	
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
	}
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
		gatherSlot(all[i]);
	}
	for (slot in found) {
		if (found[slot].length != 0) {
			for (i = 0; i < all.length; i++) {
				var arr = found[slot];
				console.log(arr[0], $(all[i][0]).text());
				if (arr[0] == $(all[i][0]).text()) {
					_priorities[arr[0]] = getInput(all[i]);
				} else {
					console.log("hoobastank");
				}
			}
				
		}
		if (_priorities["length"] == 0) {
			delete _priorities["length"];
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
}

function go(key) {
	$("#content_corner").empty();
	var div = "#list_tile_"+key;
	createContent(key);
	$(div)[0].childNodes[2].style.display = "inline-block";
	setParent($(div)[0].childNodes[2], $("#content_corner")[0]);
}