	var all_el = [];
	
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
					console.log(teams);
					console.log(teams["S"]);
					console.log(teams["A"]);
					console.log(teams["B"]);
					console.log(teams["C"]);
				} else {
					
					
				}
			}
		}
	}
	$( function() { 
		var coll = document.getElementsByClassName("expand");
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
	
	
	
	function setParent(el, newParent) {
		newParent.appendChild(el);
	}
	
	
	
	function check() {
		var element = $(event.target);
		var received = element.parent().attr('id');
		var header_received = element.attr('id');
		if ($('#'+received).parents("#mySidebar").length === 1) {
			
			setParent(document.getElementById(received), document.body);
			
			$('#'+received).offset({ top: 100, left: 100 });
			$('#'+header_received).prop("onclick", null).off("click");
			
		} else {
			
		}
	}
	function submit() {
		console.log('why');
		$.ajax({
			method: "POST",
			url: "post",
			data: {"a": "b"}
		});
		//.done(function(msg) {
		//	alert( "Data Saved: " + msg);
		//});
	}
	$(document).ready(function(){	
		
		for(i = 0; i < 2; i++) {
			var dragId = "drag_"+i;
			var element = document.getElementById('header_'+i);
			$('#mySidebar').append('<div id="drag_'+i+'" class="drag";></div>');
			var div = document.getElementById(dragId);
			$(div).append('<div id="header_'+i+'" class="header"; onclick=check();>yee</div>');
			$(div).append('<button type="button" class="expand" ></button>');
			$(div).append('<div id="content_'+i+'" class="content">Bruh </div>');
			all_el.push(div);
		}
		$(".drag").draggable({
			containment: document.body
			});
		
	});
	
	document.getElementById('open_sidebar').addEventListener("click", function(){
		document.getElementById('mySidebar').style.display = "block"; 
	});
	document.getElementById('close_sidebar').addEventListener("click", function(){
		document.getElementById('mySidebar').style.display = "none"; 
	});
