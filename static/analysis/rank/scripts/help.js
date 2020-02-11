var all_el = [];
var all_el_names = [];
var set = [];
var teamNum = "";
var json;
var attr = [];
var attr_content = [];
	
document.addEventListener("pointerup", getTierList);

var currentRank = {
	"S": [],
	"A": [],
	"B": [],
	"C": [],
};
	
var teams = {
	"S": [],
	"A": [],
	"B": [],
	"C": [],
};
function getTierList() {
	teams["S"].length = 0;
	teams["A"].length = 0;
	teams["B"].length = 0;
	teams["C"].length = 0;
	set.length = 0;
		
	for( var key in teams) {
		var d1_offset = $("#rank_"+key).offset();
		var d1_height = $("#rank_"+key).outerHeight( true );
		var d1_width = $("#rank_"+key).outerWidth( true );
		var d1_distance_from_top  = d1_offset.top + d1_height;
		var d1_distance_from_left = d1_offset.left + d1_width;
		for (i = 0; i < all_el.length;i++) {
			var d2_offset             = $(all_el[i]).offset();
			var d2_height             = $(all_el[i]).outerHeight( true );
			var d2_width              = $(all_el[i]).outerWidth( true );
			var d2_distance_from_top  = d2_offset.top + d2_height;
			var d2_distance_from_left = d2_offset.left + d2_width;
			var not_colliding = ( d1_distance_from_top < d2_offset.top || d1_offset.top > d2_distance_from_top || d1_distance_from_left < d2_offset.left || d1_offset.left > d2_distance_from_left );
			
			var both = $("#rank_"+key).add($(all_el[i]));
			var leftMost = ($("#rank_"+key).offset( ).left < $(all_el[i]).offset( ).left ? $("#rank_"+key) : $(all_el[i]));
			var rightMost = both.not( leftMost );
			var topMost = ($("#rank_"+key).offset( ).top < $(all_el[i]).offset( ).top ? $("#rank_"+key) : $(all_el[i]));
			var botMost = both.not( topMost );

			var overlap = {   'x': (leftMost.offset( ).left + leftMost.outerWidth( )) - rightMost.offset( ).left,
                  'y': (topMost.offset( ).top + topMost.outerHeight( )) - botMost.offset( ).top };
				  
			if(not_colliding === false) {
				var _team = $('#' + all_el[i].childNodes[0].id).text();
				var o_array = Object.values(overlap);
				if(o_array[1] >= $(all_el[i]).height() / 2) {
				//if(set.indexOf(_team) == -1){
					//set.push(_team);
					teams[key].push(_team);
					$.ajax({
						method: "POST",
						url: "post",
						data: {'data': JSON.stringify(teams)}
					});
				} else {
					console.log("Team duplicate error");
				}
				
			}
		}			
	}
}
			
function setParent(el, newParent) {
	newParent.appendChild(el);
}

String.prototype.insert = function (index, string) {
      if (index > 0)
        return this.substring(0, index) + string + this.substring(index, this.length);
      
      return string + this;
};

function ReplaceContentInContainer(div, content) {
    var container = div;
    container.innerHTML = content;
}
		
$(document).ready(function(){	
	var website = window.location.href;
	var partial = website.split("/analysis/rank", 2) + "/csv";
	var part_1 = partial.substring(0, 32);
	var part_2 = partial.substring(33, 37);
	var full = part_1 + part_2;
	var _left = 75;
	var _top = 0;
	var indexStorage = [];
	var w = 0;
	
	var _data = JSON.parse(window.data);
	var _ranks = JSON.parse(window.ranks);
	var _col = JSON.parse(window.col);
	
	
	$.ajax({
		url: full,
		async: false,
		success: function (csvd) {
			json = $.csv.toObjects(csvd);
		},
		dataType: "text"
	});
	
	for (i = 0; i < json.length; i++, w++) {
		teamNum = json[i].team;
		attr.length = 0;
		delete json[i]["matchnum"];
		delete json[i]["team"];
		var string;
		var data = Object.values(json[i]);
		for(y = 0; y < _col.length; y++){
			var name = _col[y]
			var _team = $($('div:contains('+teamNum+')').parent());
			if (all_el_names.indexOf(teamNum) != -1) {
				attr.push('<i>'+name+'</i>'+ ': ' + "<font color = 'red'>"+data[y]+"</font>");
				string = attr.join('<br/>');
				//console.log(_team);
				_team[2].childNodes[2].remove();
				$(_team).append('<div id="content_'+i+'" class="content">'+string+'</div>');
				
			} else {
				attr.push('<i>'+name+'</i>'+ ': ' + "<font color = 'red'>"+data[y]+"</font>");
				string = attr.join('<br/>');
			//var regex = /[:-<]/g;
			}
		}
		if(all_el_names.indexOf(teamNum) != -1) {
			//console.log($($('div:contains('+teamNum+')').parent()[2].childNodes[1]).text());//.childNodes[1]);
			console.log("Duplicate found");
		} else {
		var dragId = "drag_"+i;
		var element = document.getElementById('header_'+i);
		$('#mySidebar').append('<div id="drag_'+i+'" class="drag";></div>');
		var div = document.getElementById(dragId);
		var previous_div;
		var pre_offset;
		$(div).append('<div id="header_'+i+'" class="header"; onclick=check();>'+teamNum+'</div>');
		$(div).append('<button type="button" class="expand" ></button>');
		$(div).append('<div id="content_'+i+'" class="content">'+string+'</div>');
		
		$('#mySidebar').append(div);
		
		var num = i/16;
		var _top = 5;
		if(Number.isInteger(num)) {
			_left = _left + 5;
			w = 0;
			//_top = 5;
			//console.log(w);
			$(div).offset({top: 25, left: _left+'%'});
		} else {	
			//console.log(w);
			//_top = -5 * w;
			$(div).offset({top: 25 * (w + 1), left: _left+'%'});
			//console.log($(div).position());
		}
		all_el.push(div);
		all_el_names.push($('#' + div.childNodes[0].id).text());
		
		$.each(_ranks, function(index, value) {
			
			if($('#' + div.childNodes[0].id).text() == index){
				$(document.getElementById("sweetmotherofpearl")).append(div);
				currentRank[value].push(div);
				$(div).position({
					of: $("#rank_"+value)
				});
			}	
		});
		}
	}
	//console.log(currentRank.length);
	var result = Object.keys(currentRank).map(function(key) {
		return [String(key), currentRank[key]];
	});
	console.log(currentRank);
	var _top_ = 0;
	for (i = 0; i < result.length; i++){
		//console.log(result[i][1]);
		//_top_ = 0;
		for (y = 0; y < result[i][1].length; y++) {
			if (previous_div == null) {
				//console.log($(result[i][1][y]));
				var OffsetTop = $(result[i][1][y]).offset.top;
				$(result[i][1][y]).offset({top: OffsetTop, left: 0});
				previous_div = result[i][1][y];
				pre_offset = $(previous_div).offset().left;
			} else {
				//console.log(y);
				var num_ = (y/16);
				//console.log(num_);
				for (z = 0; z < 4; z++){
					if(	div.left >= $("#rank_"+currentRank[z]).right || div.top >= $("#rank_"+currentRank[z]).bottom || 
						div.right <= $("#rank_"+currentRank[z]).left || div.bottom <= $("#rank_"+currentRank[z]).top) {
						//console.log(num_);
						console.log($(result[i][1][y]).offset().top + 25);
						$(result[i][1][y]).offset({top: $(result[i][1][y]).offset().top + 50, left: 0})
						previous_div = result[i][1][y];
					} else {
						console.log(_top_);
						pre_offset = $(previous_div).offset().left;
						$(result[i][1][y]).offset({top: $(previous_div).offset().top + _top_, left: pre_offset + 60})
						//console.log(pre_offset + 50);
						previous_div = result[i][1][y];
					}
				}
			}
		}
		previous_div = null;
		//_top_ = 0;
		
	}
	$( ".drag" ).draggable({containment: "#sweetmotherofpearl", scroll: false });
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
	var coll = $('.expand');
	var i;
	
	for (i = 0; i < coll.length; i++) {
		coll[i].addEventListener("click", function() {
			this.classList.toggle("active");
			var content = this.nextElementSibling;
			if (content.style.display === "block") {
				content.style.display = "none";
			} else {
				content.style.display = "block";
			}
		});
	}
	//console.log(div)
	//console.log(currentRank);
});

	document.getElementById('mySidebar').style.display = "block"; 
/*document.getElementById('open_sidebar').addEventListener("click", function(){
	document.getElementById('mySidebar').style.display = "block"; 
});
document.getElementById('close_sidebar').addEventListener("click", function(){
	document.getElementById('mySidebar').style.display = "none"; 
});*/
