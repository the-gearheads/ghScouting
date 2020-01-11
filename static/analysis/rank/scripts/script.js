var all_el = [];
	document.addEventListener("mouseup", getTierList());
	
	function getTierList() {
		var teams = {
			"S": [],
			"A": [],
			"B": [],
			"C": [],
		}
		for( var key in teams) {
			console.log(key);
			console.log("#rank_"+key);
			console.log(document.getElementById("rank_"+key));
			var rect2 = document.getElementById("rank_"+key).getBoundingClientRect();
			for (i = 0; i < all_el.length;i++) {
				var rect1 = all_el[i].getBoundingClientRect();
				var overlap = !(rect1.right < rect2.left || 
                rect1.left > rect2.right || 
                rect1.bottom < rect2.top || 
                rect1.top > rect2.bottom);
				if(overlap === false) {
					teams[key].push(all_el[i]);
				} else {
					
				}
			}	
			console.log(teams[key]);
		}
	}
	$( function() { 
		
			<!--snap: ".slot", snapMode:"inner"-->
		
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
	
	function openNav() {
		document.getElementById("mySidebar").style.display = "block";
		
	}
	function closeNav() {
		document.getElementById("mySidebar").style.display = "none";
		
	}
	
	function setParent(el, newParent) {
		newParent.appendChild(el);
	}
	
	
	
	function check() {
		var element = $(event.target);
		console.log(element.parent());
		var received = element.parent().attr('id');
		var header_received = element.attr('id');
		console.log('#'+received);
		if ($('#'+received).parents("#mySidebar").length === 1) {
			
			setParent(document.getElementById(received), document.body);
			
			$('#'+received).offset({ top: 100, left: 100 });
			$('#'+header_received).prop("onclick", null).off("click");
			console.log("yes");
			
		} else {
			console.log("no");
		}
		}
	function make_tierlist() {
		
	}
	function submit() {
	$.ajax({
		method: "POST",
		url: "post",
		data: { name: "John"}
		})
		.done(function(msg) {
			alert( "Data Saved: " + msg);
		});
		}
	$(document).ready(function(){	
		for(i = 0; i < 2; i++) {
			var dragId = "drag_"+i;
			var element = document.getElementById('header_'+i);
			console.log(dragId);
			$('#mySidebar').append('<div id="drag_'+i+'" class="drag";></div>');
			var div = document.getElementById(dragId);
			$(div).append('<div id="header_'+i+'" class="header"; onclick=check();>yee</div>');
			console.log("Header complete");
			$(div).append('<button type="button" class="expand" ></button>');
			console.log("button complete");
			$(div).append('<div id="content_'+i+'" class="content">Bruh </div>');
			console.log("content complete");
			all_el.push(div);
		}
		$(".drag").draggable({
			containment: document.body
			});
		
	});