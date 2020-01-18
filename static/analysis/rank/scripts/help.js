var all_el = [];
var teamNum = "";
var json;
var attr = [];
var attr_content = [];
	
document.addEventListener("pointerup", getTierList);
	
var teams = {
	"S": [],
	"A": [],
	"B": [],
	"C": [],
}
function getTierList() {
	teams["S"].length = 0;
	teams["A"].length = 0;
	teams["B"].length = 0;
	teams["C"].length = 0;
		
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
			
			if(not_colliding === false) {
				teams[key].push($('#' + all_el[i].childNodes[0].id).text());
				$.ajax({
					method: "POST",
					url: "post",
					data: {'data': JSON.stringify(teams)}
				});
					
				console.log(teams["S"]);
				console.log(teams["A"]);
				console.log(teams["B"]);
				console.log(teams["C"]);
			} else {
				
				
			}
		}
	}
}

		
function setParent(el, newParent) {
	newParent.appendChild(el);
}
		
$(document).ready(function(){	
	var website = window.location.href;
	var partial = website.split("/analysis/rank", 2) + "/csv";
	var part_1 = partial.substring(0, 32);
	var part_2 = partial.substring(33, 37);
	var full = part_1 + part_2;
	$.ajax({
		url: full,
		async: false,
		success: function (csvd) {
			json = $.csv.toObjects(csvd);
			
		},
		dataType: "text"
	});
	console.log(full);
	for (i = 0; i < json.length; i++) {
		teamNum = json[i].team;
		attr.length = 0;
		var data = Object.values(json[i]);
		var name = Object.getOwnPropertyNames(json[i]);
		for(y = 2; y < data.length; y++){
			attr.push('<b>'+name[y]+'</b>'+ ': ' + data[y]);
			string = attr.join('<br/>');
		}
	
		console.log(json[i]);
		console.log(Object.values(json[i]));
		console.log(name);
		console.log(attr);
		var dragId = "drag_"+i;
		var element = document.getElementById('header_'+i);
		$('#mySidebar').append('<div id="drag_'+i+'" class="drag";></div>');
		var div = document.getElementById(dragId);
		$(div).append('<div id="header_'+i+'" class="header"; onclick=check();>'+teamNum+'</div>');
		$(div).append('<button type="button" class="expand" ></button>');
		$(div).append('<div id="content_'+i+'" class="content">'+string+'</div>');
		$(div).offset({top: 75 * (i + 1), left: 10});
		all_el.push(div);
			
	}
		
	$( ".drag" ).draggable();
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
});

	
document.getElementById('open_sidebar').addEventListener("click", function(){
	document.getElementById('mySidebar').style.display = "block"; 
});
document.getElementById('close_sidebar').addEventListener("click", function(){
	document.getElementById('mySidebar').style.display = "none"; 
});
