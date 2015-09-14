/*Aggelos Javascript/jQuery */

var SERVER_URL = "http://127.0.0.1:8000";
var BASE_URL = SERVER_URL + "/activitytracker/";

function Loading(){
	$("#overlay").show();
}

function LoadingWithBackdrop(){
	$("#overlay").show();
	$('<div class="modal-backdrop"></div>').appendTo(document.body);
}

function WaitFunctionToLoad(e){
    $("#overlay").show();
	$('<div class="modal-backdrop"></div>').appendTo(document.body);
    WaitForFunction(e);
}

function WaitForFunction(e)
{
    if (!$.isFunction(e)) {
       setTimeout( WaitForFunction, 100);
       return;
    }
   $("#overlay").hide();
   $(".modal-backdrop").remove();
}

function Done(){
	$("#overlay").hide();
}

function DoneWithBackdrop(){
	$("#overlay").hide();
	$(".modal-backdrop").remove();
}

function ShownIds(){
	var list = [];
	var IdString = "";
	list = $(".activity-flag").map(function(){
		return $(this).attr("id");
	}).get();
	return list.join('_');
}

function plotDonutChart(data){
		$.plot($("#donutchart"), data,
			{
				series: {
					pie: {
						innerRadius: 0.5,
						show: true
					}
				},
				legend: {
					show: false
				},
				colors: ["#FA5833", "#2FABE9", "#FABB3D", "#78CD51"]
			});

	}

function drawDonut() {
	$.ajax({
				type: "get",
				global: false,
				data: {chart_data: ShownIds(), csrfmiddlewaretoken: getCookie('csrftoken')},
				url: BASE_URL + "index/chartdatajson/",
				dataType: "json",
				success: function (data) {
					plotDonutChart(data);
				},
				error: function(){
					alert('Client did not receive a response. Reloading page')
					window.location.reload();
				}
			});
};

function submitFields(form, csrf ) {
	 var activity = document.forms[form]["name_of_activity"].value;
	 var start = document.forms[form]["start_time"].value;
	 var end = document.forms[form]["end_time"].value;
	 var start_date = document.forms[form]["start_date"].value;
	 var end_date = document.forms[form]["end_date"].value;
	 try {
		 var friends = $('#' + form.toString() + ' select[name=friends]').val().toString();
	 }
	 catch (e){
		var friends = ""
	 }
	 try {
		 var tools = $('#'+ form.toString() +' select[name=tools]').val().toString();
	 }
	 catch (e){
		var tools = ""
	 }
 	 var goal = document.forms[form]["goal"].value;
	 var result = document.forms[form]["result"].value;
	 var location_address = document.forms[form]["location"].value;
	 var data_return =  { name_of_activity: activity,
						start_date: start_date,
						end_date: end_date,
						start_time: start,
						end_time: end,
						friend_list: friends,
						tool: tools,
						goal: goal,
		 				result: result,
		 				location_address: location_address,
						csrfmiddlewaretoken: csrf
					  };
	if (goal != ""){
		 data_return.goalstatus = document.forms[form]["goalstatus"].value;
	 }
	return data_return
};

function eraseActivity(id){
	$("#" + id).remove();
};

function eraseAllActivities(){
	$(".activity-flag").remove();
};

function drawActivity(e) {
	var new_activity = document.createElement("a");
	var classes = 'quick-button metro span4b activity-flag ' + e.colour;
	var remote_url = '/activitytracker/activity/display-activity/' + e.id;
	var icon = document.createElement('i');
	var act_name = document.createElement('p');
	var name_text = document.createTextNode(e.activity);
	var durationSpan = document.createElement('span');
	var duration_text = document.createTextNode(e.duration);
	durationSpan.className = 'badge';
	icon.className = 'activicon-' + e.icon_classname;
	durationSpan.appendChild(duration_text);
	act_name.appendChild(name_text);
	new_activity.appendChild(icon);
	new_activity.appendChild(durationSpan);
	new_activity.appendChild(act_name);
	new_activity.href = remote_url;
	new_activity.id = e.id;
	new_activity.className = classes;
	$(new_activity).attr("data-target", "#showActivityModal");
	$(new_activity).attr("data-toggle", "modal");

	if ($('.span6b .activity-flag').length < 9) {
		first_row = $('.span6b .row-fluid')[0];
		second_row = $('.span6b .row-fluid')[1];
		third_row = $('.span6b .row-fluid')[2];

		if ($(first_row).find('.activity-flag').length < 3) {
			$(first_row).append(new_activity);
		}
		else if ($(second_row).find('.activity-flag').length < 3) {
			$(second_row).append(new_activity);
		}
		else {
			$(third_row).append(new_activity);
		}
	}
	else {
		var counter = 0;
		var rowId = 'rest' + counter.toString();
		new_activity.className = 'quick-button metro span2 activity-flag ' + e.colour;
		$(new_activity).css('margin-right','2.35%');
		try {
			while ((document.getElementById(rowId).getElementsByClassName("activity-flag")).length == 6) {
				counter += 1;
				rowId = 'rest' + counter.toString();
			}
			if ((document.getElementById(rowId).getElementsByClassName("activity-flag")).length == 5) {
				$(new_activity).css('margin-right','0%');
			}
			var row = document.getElementById(rowId);
			row.appendChild(new_activity);
		}
		catch (err) {
			var divN = document.createElement('div');
			divN.className = 'row-fluid';
			divN.id = rowId;
			divN.appendChild(new_activity);
			var father = document.getElementById('content-rest');
			father.appendChild(divN);
		}

	}
	return;
}
/* Draws the Grouped or Ungrouped Data */
function DrawGroupUngroupSort(id_list) {
	if (document.getElementById('groupcheckbox').checked) {
		var data = {grouped_data: id_list, box: "checked", sort: $('#sortdropdown').val(), csrfmiddlewaretoken: getCookie('csrftoken')}
	}
	else {
		var data = {grouped_data: id_list, box: "unchecked", sort: $('#sortdropdown').val(), csrfmiddlewaretoken: getCookie('csrftoken')}
	}
	$.ajax({
		type: "post",
		data: data,
		cache: false,
		url: BASE_URL + "index/getgroupedactivities/",
		dataType: "json",
		error: function (xhr, status, error) {
			Done();
			alert(xhr.responseText);
		},
		success: function (responseJSON) {
			eraseAllActivities();
			$.each(responseJSON, function(i, e){ 
				drawActivity(e);
				if (document.getElementById('groupcheckbox').checked && (e.id).indexOf("_") != -1) {
					$('#'+ e.id).attr("data-target", "#showGroupActivityModal");
					$('#'+ e.id).attr("href", '/activitytracker/activity/display-group-activity/' + e.id);
					$('#'+ e.id + ' span').text('Total: '+ e.duration)
				}
			});
			//drawAddAnotherButton();
		}
	});
}

/* Draws the Grouped or Ungrouped Data and then fills the Donut Chart*/
function DrawGroupUngroupSortWithChart(id_list) {
	if (document.getElementById('groupcheckbox').checked) {
		var data = {grouped_data: id_list, box: "checked", sort: $('#sortdropdown').val(), csrfmiddlewaretoken: getCookie('csrftoken')}
	}
	else {
		var data = {grouped_data: id_list, box: "unchecked", sort: $('#sortdropdown').val(), csrfmiddlewaretoken: getCookie('csrftoken')}
	}
	$.ajax({
		type: "post",
		data: data,

		cache: false,
		url: BASE_URL + "index/getgroupedactivities/",
		dataType: "json",
		error: function (xhr, status, error) {
			Done();
			alert(xhr.responseText);
		},
		success: function (responseJSON) {
			eraseAllActivities();
			$.each(responseJSON, function(i, e){
				drawActivity(e);
				if (document.getElementById('groupcheckbox').checked && (e.id).indexOf("_") != -1) {
					$('#'+ e.id).attr("data-target", "#showGroupActivityModal");
					$('#'+ e.id).attr("href", '/activitytracker/activity/display-group-activity/' + e.id);
					$('#'+ e.id + ' span').text('Total: '+ e.duration)
				}
			});
			//drawAddAnotherButton();
			drawDonut();
		}
	});
}

function CalendarDaterange(viewInstance){
	var day,month,year,day2,month2,year2;
	var period = String(viewInstance.title.replace('&#8212;',"-"));
	var mode = String(viewInstance.name);
	if (mode == "agendaDay"){
		var dateparts = period.split(",");
		year = dateparts[2].replace(/ /g, "");
		month = (dateparts[1].split(" "))[1];
		day = (dateparts[1].split(" "))[2];
		if (day.length == 1){
			day = "0"+day;
		}
		return {mode:mode, day: day, month: month, year: year}
	}
	else if (mode == "month"){
		year = (period.split(" "))[1];
		month = ((period.split(" "))[0]).substring(0,3);
		return {mode:mode, month:month, year:year}
	}
	else{
		if ( period.length <= 17){ //same month
			var range = period.split("-");
			month = (range[0].split(" "))[0];
			day = (range[0].split(" "))[1];
			day2 = (range[1].split(" "))[1];
			year = (range[1].split(" "))[2];
			if (day.length == 1){
				day = "0" + day;
			}
			if (day2.length == 1){
				day2 = "0" + day2
			}
			return{ mode:mode, day: day, month: month, year:year, day2: day2, month2:month, year2:year}
		}
		else if (period.length == 19) { //between months & same year
			var range = period.split("-");
			month = (range[0].split(" "))[0];
			day = (range[0].split(" "))[1];
			month2 = (range[1].split(" "))[1];
			day2 = (range[1].split(" "))[2];
			year2 = (range[1].split(" "))[3];
			day2 = "0" + day2; // this day would have only 1 digit, due to being between months
			return {mode: mode, day: day, month: month, year: year2, day2: day2, month2: month2, year2: year2}
		}
		else{  // diff months & diff years
			var range = period.split("-");
			month = (range[0].split(" "))[0];
			day = (range[0].split(" "))[1];
			year = (range[0].split(" "))[2];
			month2 = (range[1].split(" "))[1];
			day2 = (range[1].split(" "))[2];
			year2 = (range[1].split(" "))[3];
			return{ mode:mode, day: day, month: month, year:year, day2: day2, month2:month2, year2:year2}
			}
	}
}

/* redraws Activities based on view */
function RenderViewActivities(view){
	var data = CalendarDaterange(view);
	data.csrfmiddlewaretoken = getCookie('csrftoken');
	Loading();
	 $.ajax({
		 type: "post",
		 data: data,
		 cache: false,
		 url: BASE_URL + "index/displayperiod/",
		 dataType: "text",
		 error: function (xhr, status, error) {
			 Done();
			 alert('Internal Server Error. Page will be reloaded');
			 window.location.reload();
		 },
		 success: function (responseString) {
			 DrawGroupUngroupSortWithChart(responseString);
			 Done();
		 }
	 });
}

/* Check whether newly added Activity should be displayed on the view it was added on*/
function CheckDisplay(activityData){
	var CurrentView = $('#main_calendar').fullCalendar('getView');
	var data = CalendarDaterange(CurrentView);
	data.csrfmiddlewaretoken = getCookie('csrftoken');
	Loading();
	 $.ajax({
		 type: "post",
		 data: data,
		 cache: false,
		 url: BASE_URL + "index/displayperiod/",
		 dataType: "text",
		 error: function (xhr, status, error) {
			 Done();
			 alert('Internal Server Error. Page will be reloaded');
			 window.location.reload();
		 },
		 success: function (responseString) {
			 if (responseString.indexOf(activityData.id) != -1) {
				 drawActivity(activityData); // draw the activity
				 drawDonut(); // re-draw chart
			 }
		 }
	 });
}

function validateMail() {
    var x = document.forms["editUserForm"]["email"].value;
    var atpos = x.indexOf("@");
    var dotpos = x.lastIndexOf(".");
    if (atpos< 1 || dotpos<atpos+2 || dotpos+2>=x.length) {
        alert("Sorry but this is not a valid e-mail address");
        return false;
    }
}

function clearFields() {
	var start_date = document.forms["addForm"]["start_date"];
	start_date.value = "";
	var end_date = document.forms["addForm"]["end_date"];
	end_date.value = "";
	var start_time = document.forms["addForm"]["start_time"];
	start_time.value = "";
}


function getCookie(name) {
    var cookieValue = null;
    if ((document.cookie) && (document.cookie != '')) {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/*Aggelos Javascript/jQuery END */

/* -------------------- Check Browser --------------------- */

function browser() {
	
	var isOpera = !!(window.opera && window.opera.version);  // Opera 8.0+
	var isFirefox = testCSS('MozBoxSizing');                 // FF 0.8+
	var isSafari = Object.prototype.toString.call(window.HTMLElement).indexOf('Constructor') > 0;
	    // At least Safari 3+: "[object HTMLElementConstructor]"
	var isChrome = !isSafari && testCSS('WebkitTransform');  // Chrome 1+
	//var isIE = /*@cc_on!@*/false || testCSS('msTransform');  // At least IE6

	function testCSS(prop) {
	    return prop in document.documentElement.style;
	}
	
	if (isOpera) {
		
		return false;
		
	}else if (isSafari || isChrome) {
		
		return true;
		
	} else {
		
		return false;
		
	}
	
}

/* ---------- IE8 list style hack (:nth-child(odd)) ---------- */

jQuery(document).ready(function($){
	
	if($('.messagesList').width()) {
		
		if(jQuery.browser.version.substring(0, 2) == "8.") {

			$('ul.messagesList li:nth-child(2n+1)').addClass('odd');
			
		}
		
	}
	
});	

$(document).ready(function(){
		
			
	$("#username").focus(function() {
		
		$(this).parent(".input-prepend").addClass("input-prepend-focus");
	
	});
	
	$("#username").focusout(function() {
		
		$(this).parent(".input-prepend").removeClass("input-prepend-focus");
	
	});
	
	$("#password").focus(function() {
		
		$(this).parent(".input-prepend").addClass("input-prepend-focus");
	
	});
	
	$("#password").focusout(function() {
		
		$(this).parent(".input-prepend").removeClass("input-prepend-focus");
	
	});
	
				
	/* ---------- Add class .active to current link  ---------- */
	$('ul.main-menu li a').each(function(){
		
			if($($(this))[0].href==String(window.location)) {
				
				$(this).parent().addClass('active');
				
			}
	
	});
	
	$('ul.main-menu li ul li a').each(function(){
		
			if($($(this))[0].href==String(window.location)) {
				
				$(this).parent().addClass('active');
				$(this).parent().parent().show();
				
			}
	
	});
	
	/* ---------- Submenu  ---------- */
	
	$('.dropmenu').click(function(e){

		e.preventDefault();

		$(this).parent().find('ul').slideToggle();
	
	});
			
	/* ---------- Acivate Functions ---------- */
	template_functions();
	charts();
	calendars();
	widthFunctions();

});

/* ---------- Like/Dislike ---------- */


/* ---------- Check Retina ---------- */

function retina(){
	
	retinaMode = (window.devicePixelRatio > 1);
	
	return retinaMode;
	
}


/* ---------- Numbers Sepparator ---------- */

function numberWithCommas(x) {
    x = x.toString();
    var pattern = /(-?\d+)(\d{3})/;
    while (pattern.test(x))
        x = x.replace(pattern, "$1.$2");
    return x;
}

/* ---------- Template Functions ---------- */		
		
function template_functions(){
	
	/* ---------- ToDo List Action Buttons ---------- */
	
	$(".todo-remove").click(function(){
		
		$(this).parent().parent().fadeTo("slow", 0.00, function(){ //fade
			$(this).slideUp("slow", function() { //slide up
		    	$(this).remove(); //then remove from the DOM
		    });
		});
		
		
		return false;
	});
	
	$(".todo-list").find('.action').each(function(){
		
		$(this).click(function(){
			
			if($(this).hasClass('icon-check-empty')) {
				
				$(this).removeClass('icon-check-empty');
				$(this).addClass('icon-check');
				
				$(this).parent().css('text-decoration','line-through');
				
			} else {
				
				$(this).removeClass('icon-check');
				$(this).addClass('icon-check-empty');
				
				$(this).parent().css('text-decoration','none');
				
			}
			
			return false;
			
		});
		
	});
	
	

	/* ---------- Skill Bars ---------- */
	$(".meter > span").each(function() {
		
		var getColor = $(this).parent().css('borderTopColor');
				
		$(this).css('background',getColor);
		
		$(this)
		.data("origWidth", $(this).width())
		.width(0)
		.animate({
			width: $(this).data("origWidth")
		}, 3000);
	});
	
	/* ---------- Disable moving to top ---------- */
	$('a[href="#"][data-top!=true]').click(function(e){
		e.preventDefault();
	});
	
	/* ---------- Datapicker ---------- */
	$('.datepicker').datepicker();
	
	/* ---------- Notifications ---------- */
	$('.noty').click(function(e){
		e.preventDefault();
		var options = $.parseJSON($(this).attr('data-noty-options'));
		noty(options);
	});

	/* ---------- Uniform ---------- */
	$("input:checkbox, input:radio, input:file").not('[data-no-uniform="true"],#uniform-is-ajax').uniform();

	/* ---------- Choosen ---------- */
	$('[data-rel="chosen"],[rel="chosen"]').chosen();

	/* ---------- Tabs ---------- */
	$('#myTab a:first').tab('show');
	$('#myTab a').click(function (e) {
	  e.preventDefault();
	  $(this).tab('show');
	});

	/* ---------- Makes elements soratble, elements that sort need to have id attribute to save the result ---------- */
	$('.sortable').sortable({
		revert:true,
		cancel:'.btn,.box-content,.nav-header',
		update:function(event,ui){
			//line below gives the ids of elements, you can make ajax call here to save it to the database
			//console.log($(this).sortable('toArray'));
		}
	});

	/* ---------- Tooltip ---------- */
	$('[rel="tooltip"],[data-rel="tooltip"]').tooltip({"placement":"bottom",delay: { show: 400, hide: 200 }});

	/* ---------- Popover ---------- */
	$('[rel="popover"],[data-rel="popover"]').popover();


	/* ---------- Fullscreen ---------- */
	$('#toggle-fullscreen').button().click(function () {
		var button = $(this), root = document.documentElement;
		if (!button.hasClass('active')) {
			$('#thumbnails').addClass('modal-fullscreen');
			if (root.webkitRequestFullScreen) {
				root.webkitRequestFullScreen(
					window.Element.ALLOW_KEYBOARD_INPUT
				);
			} else if (root.mozRequestFullScreen) {
				root.mozRequestFullScreen();
			}
		} else {
			$('#thumbnails').removeClass('modal-fullscreen');
			(document.webkitCancelFullScreen ||
				document.mozCancelFullScreen ||
				$.noop).apply(document);
		}
	});


	$('.btn-close').click(function(e){
		e.preventDefault();
		$(this).parent().parent().parent().fadeOut();
	});
	$('.btn-minimize').click(function(e){
		e.preventDefault();
		var $target = $(this).parent().parent().next('.box-content');
		if($target.is(':visible')) $('i',$(this)).removeClass('chevron-up').addClass('chevron-down');
		else 					   $('i',$(this)).removeClass('chevron-down').addClass('chevron-up');
		$target.slideToggle();
	});
	$('.btn-setting').click(function(e){
		e.preventDefault();
		$('#myModal').modal('show');
	});


	
	/* ---------- Custom Slider ---------- */
		$(".sliderSimple").slider();

		$(".sliderMin").slider({
			range: "min",
			value: 180,
			min: 1,
			max: 700,
			slide: function( event, ui ) {
				$( ".sliderMinLabel" ).html( "$" + ui.value );
			}
		});

		$(".sliderMin-1").slider({
			range: "min",
			value: 50,
			min: 1,
			max: 700,
			slide: function( event, ui ) {
				$( ".sliderMin1Label" ).html( "$" + ui.value );
			}
		});

		$(".sliderMin-2").slider({
			range: "min",
			value: 100,
			min: 1,
			max: 700,
			slide: function( event, ui ) {
				$( ".sliderMin2Label" ).html( "$" + ui.value );
			}
		});

		$(".sliderMin-3").slider({
			range: "min",
			value: 150,
			min: 1,
			max: 700,
			slide: function( event, ui ) {
				$( ".sliderMin3Label" ).html( "$" + ui.value );
			}
		});

		$(".sliderMin-4").slider({
			range: "min",
			value: 250,
			min: 1,
			max: 700,
			slide: function( event, ui ) {
				$( ".sliderMin4Label" ).html( "$" + ui.value );
			}
		});

		$(".sliderMin-5").slider({
			range: "min",
			value: 350,
			min: 1,
			max: 700,
			slide: function( event, ui ) {
				$( ".sliderLabel" ).html( "$" + ui.value );
			}
		});
		
		$(".sliderMin-6").slider({
			range: "min",
			value: 450,
			min: 1,
			max: 700,
			slide: function( event, ui ) {
				$( ".sliderLabel" ).html( "$" + ui.value );
			}
		});
		
		$(".sliderMin-7").slider({
			range: "min",
			value: 550,
			min: 1,
			max: 700,
			slide: function( event, ui ) {
				$( ".sliderLabel" ).html( "$" + ui.value );
			}
		});
		
		$(".sliderMin-8").slider({
			range: "min",
			value: 650,
			min: 1,
			max: 700,
			slide: function( event, ui ) {
				$( ".sliderLabel" ).html( "$" + ui.value );
			}
		});
		
		
		$(".sliderMax").slider({
			range: "max",
			value: 280,
			min: 1,
			max: 700,
			slide: function( event, ui ) {
				$( ".sliderMaxLabel" ).html( "$" + ui.value );
			}
		});

		$( ".sliderRange" ).slider({
			range: true,
			min: 0,
			max: 500,
			values: [ 192, 470 ],
			slide: function( event, ui ) {
				$( ".sliderRangeLabel" ).html( "$" + ui.values[ 0 ] + " - $" + ui.values[ 1 ] );
			}
		});

		$( "#sliderVertical-1" ).slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: 100,
			value: 60,
		});

		$( "#sliderVertical-2" ).slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: 100,
			value: 40,
		});

		$( "#sliderVertical-3" ).slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: 100,
			value: 30,
		});

		$( "#sliderVertical-4" ).slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: 100,
			value: 15,
		});

		$( "#sliderVertical-5" ).slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: 100,
			value: 40,
		});

		$( "#sliderVertical-6" ).slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: 100,
			value: 80,
		});
		
		$( "#sliderVertical-7" ).slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: 100,
			value: 60,
		});

		$( "#sliderVertical-8" ).slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: 100,
			value: 40,
		});

		$( "#sliderVertical-9" ).slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: 100,
			value: 30,
		});

		$( "#sliderVertical-10" ).slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: 100,
			value: 15,
		});

		$( "#sliderVertical-11" ).slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: 100,
			value: 40,
		});

		$( "#sliderVertical-12" ).slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: 100,
			value: 80,
		});
			
}

      

/* ---------- Calendars ---------- */

function calendars(){
	

	$('#external-events div.external-event').each(function() {

		// it doesn't need to have a start or end
		var eventObject = {
			title: $.trim($(this).text()) // use the element's text as the event title
		};
		
		// store the Event Object in the DOM element so we can get to it later
		$(this).data('eventObject', eventObject);
		
		// make the event draggable using jQuery UI
		$(this).draggable({
			zIndex: 999,
			revert: true,      // will cause the event to go back to its
			revertDuration: 0  //  original position after the drag
		});
		
	});
	
	var date = new Date();
	var d = date.getDate();
	var m = date.getMonth();
	var y = date.getFullYear();


	if ($('#main_calendar').length == 0) return;

	$('#main_calendar').fullCalendar({
		viewRender: function(view, element) {
			RenderViewActivities(view);
		},
		header: {
			left: 'title',
			right: 'prev,next today,month,agendaWeek,agendaDay'
		},
		dayClick: function(date, view) {

			var start_date_default = $.fullCalendar.formatDate(date, "MM/dd/yyyy");
			var end_date_default = start_date_default;
			var start_time_default = $.fullCalendar.formatDate(date, "HH:mm");

        	var start_date = document.forms["addForm"]["start_date"];
			start_date.value = start_date_default;
			var end_date = document.forms["addForm"]["end_date"];
			end_date.value = end_date_default;
			if (start_time_default != "00:00") {
				var start_time = document.forms["addForm"]["start_time"];
				start_time.value = start_time_default;
			}
			$('#addActivityModal').modal('show');

		},
		 eventClick : function(event, element ){
			 $('#showActivityModal').modal({
			  remote: BASE_URL + "activity/display-activity/"+ String(event.id) +"/"
		   });
  		 },
		aspectRatio: 1.5,
		editable: true,
		events: BASE_URL + "index/eventstojson/"
	});
}


/* ---------- Charts ---------- */

function charts() {
	
	function randNum(){
		return ((Math.floor( Math.random()* (1+40-20) ) ) + 20)* 1200;
	}
	
	function randNum2(){
		return ((Math.floor( Math.random()* (1+40-20) ) ) + 20) * 500;
	}
	
	function randNum3(){
		return ((Math.floor( Math.random()* (1+40-20) ) ) + 20) * 300;
	}
	
	function randNum4(){
		return ((Math.floor( Math.random()* (1+40-20) ) ) + 20) * 100;
	}
	
	/* ---------- Chart with points ---------- */


		function showTooltip(x, y, contents) {
			$('<div id="tooltip">' + contents + '</div>').css( {
				position: 'absolute',
				display: 'none',
				top: y + 5,
				left: x + 5,
				border: '1px solid #fdd',
				padding: '2px',
				'background-color': '#dfeffc',
				opacity: 0.80
			}).appendTo("body").fadeIn(200);
		}

		var previousPoint = null;

	
	function randNumFB(){
		return ((Math.floor( Math.random()* (1+40-20) ) ) + 20);
	}

	
	function randNumTW(){
		return ((Math.floor( Math.random()* (1+40-20) ) ) + 20);
	}

	
	/* ---------- Flot chart ---------- */
	if($("#flotchart").length)
	{
		var d1 = [];
		for (var i = 0; i < Math.PI * 2; i += 0.25)
			d1.push([i, Math.sin(i)]);
		
		var d2 = [];
		for (var i = 0; i < Math.PI * 2; i += 0.25)
			d2.push([i, Math.cos(i)]);

		var d3 = [];
		for (var i = 0; i < Math.PI * 2; i += 0.1)
			d3.push([i, Math.tan(i)]);
		
		$.plot($("#flotchart"), [
			{ label: "sin(x)",  data: d1},
			{ label: "cos(x)",  data: d2},
			{ label: "tan(x)",  data: d3}
		], {
			series: {
				lines: { show: true },
				points: { show: true }
			},
			xaxis: {
				ticks: [0, [Math.PI/2, "\u03c0/2"], [Math.PI, "\u03c0"], [Math.PI * 3/2, "3\u03c0/2"], [Math.PI * 2, "2\u03c0"]]
			},
			yaxis: {
				ticks: 10,
				min: -2,
				max: 2
			},
			grid: {	tickColor: "#dddddd",
					borderWidth: 0 
			},
			colors: ["#FA5833", "#2FABE9", "#FABB3D"]
		});
	}

	
	/* ---------- Device chart ---------- */
	
	var data = [
	{ label: "Desktop",  data: 73},
	{ label: "Mobile",  data: 27}
	];

	/* ---------- Pie chart ---------- */
	
	if($("#piechart").length)
	{
		$.plot($("#piechart"), data,
		{
			series: {
					pie: {
							show: true
					}
			},
			grid: {
					hoverable: true,
					clickable: true
			},
			legend: {
				show: false
			},
			colors: ["#FA5833", "#2FABE9", "#FABB3D", "#78CD51"]
		});
		
		function pieHover(event, pos, obj)
		{
			if (!obj)
					return;
			percent = parseFloat(obj.series.percent).toFixed(2);
			$("#hover").html('<span style="font-weight: bold; color: '+obj.series.color+'">'+obj.series.label+' ('+percent+'%)</span>');
			$('#hover').css({'position':'absolute','display':'block','left':pos.pageX,'top':pos.pageY});
		}

		$("#piechart").bind("plothover", pieHover);

	}
	
	/* ---------- Donut chart ---------- */
	/* if ($('#donutchart').length) {
	 	drawDonut();
	 } */

	$('#donut-canvas').on('resize',function() {
   		drawDonut();
	});
	/* end donut chart */

	 // we use an inline data source in the example, usually data would
	// be fetched from a server
	var data = [], totalPoints = 300;
	function getRandomData() {
		if (data.length > 0)
			data = data.slice(1);

		// do a random walk
		while (data.length < totalPoints) {
			var prev = data.length > 0 ? data[data.length - 1] : 50;
			var y = prev + Math.random() * 10 - 5;
			if (y < 0)
				y = 0;
			if (y > 100)
				y = 100;
			data.push(y);
		}

		// zip the generated y values with the x values
		var res = [];
		for (var i = 0; i < data.length; ++i)
			res.push([i, data[i]])
		return res;
	}

	// setup control widget
	var updateInterval = 30;
	$("#updateInterval").val(updateInterval).change(function () {
		var v = $(this).val();
		if (v && !isNaN(+v)) {
			updateInterval = +v;
			if (updateInterval < 1)
				updateInterval = 1;
			if (updateInterval > 2000)
				updateInterval = 2000;
			$(this).val("" + updateInterval);
		}
	});

}


/* ---------- Additional functions for data table ---------- */
$.fn.dataTableExt.oApi.fnPagingInfo = function ( oSettings )
{
	return {
		"iStart":         oSettings._iDisplayStart,
		"iEnd":           oSettings.fnDisplayEnd(),
		"iLength":        oSettings._iDisplayLength,
		"iTotal":         oSettings.fnRecordsTotal(),
		"iFilteredTotal": oSettings.fnRecordsDisplay(),
		"iPage":          Math.ceil( oSettings._iDisplayStart / oSettings._iDisplayLength ),
		"iTotalPages":    Math.ceil( oSettings.fnRecordsDisplay() / oSettings._iDisplayLength )
	};
}
$.extend( $.fn.dataTableExt.oPagination, {
	"bootstrap": {
		"fnInit": function( oSettings, nPaging, fnDraw ) {
			var oLang = oSettings.oLanguage.oPaginate;
			var fnClickHandler = function ( e ) {
				e.preventDefault();
				if ( oSettings.oApi._fnPageChange(oSettings, e.data.action) ) {
					fnDraw( oSettings );
				}
			};

			$(nPaging).addClass('pagination').append(
				'<ul>'+
					'<li class="prev disabled"><a href="#">&larr; '+oLang.sPrevious+'</a></li>'+
					'<li class="next disabled"><a href="#">'+oLang.sNext+' &rarr; </a></li>'+
				'</ul>'
			);
			var els = $('a', nPaging);
			$(els[0]).bind( 'click.DT', { action: "previous" }, fnClickHandler );
			$(els[1]).bind( 'click.DT', { action: "next" }, fnClickHandler );
		},

		"fnUpdate": function ( oSettings, fnDraw ) {
			var iListLength = 5;
			var oPaging = oSettings.oInstance.fnPagingInfo();
			var an = oSettings.aanFeatures.p;
			var i, j, sClass, iStart, iEnd, iHalf=Math.floor(iListLength/2);

			if ( oPaging.iTotalPages < iListLength) {
				iStart = 1;
				iEnd = oPaging.iTotalPages;
			}
			else if ( oPaging.iPage <= iHalf ) {
				iStart = 1;
				iEnd = iListLength;
			} else if ( oPaging.iPage >= (oPaging.iTotalPages-iHalf) ) {
				iStart = oPaging.iTotalPages - iListLength + 1;
				iEnd = oPaging.iTotalPages;
			} else {
				iStart = oPaging.iPage - iHalf + 1;
				iEnd = iStart + iListLength - 1;
			}

			for ( i=0, iLen=an.length ; i<iLen ; i++ ) {
				// remove the middle elements
				$('li:gt(0)', an[i]).filter(':not(:last)').remove();

				// add the new list items and their event handlers
				for ( j=iStart ; j<=iEnd ; j++ ) {
					sClass = (j==oPaging.iPage+1) ? 'class="active"' : '';
					$('<li '+sClass+'><a href="#">'+j+'</a></li>')
						.insertBefore( $('li:last', an[i])[0] )
						.bind('click', function (e) {
							e.preventDefault();
							oSettings._iDisplayStart = (parseInt($('a', this).text(),10)-1) * oPaging.iLength;
							fnDraw( oSettings );
						} );
				}

				// add / remove disabled classes from the static elements
				if ( oPaging.iPage === 0 ) {
					$('li:first', an[i]).addClass('disabled');
				} else {
					$('li:first', an[i]).removeClass('disabled');
				}

				if ( oPaging.iPage === oPaging.iTotalPages-1 || oPaging.iTotalPages === 0 ) {
					$('li:last', an[i]).addClass('disabled');
				} else {
					$('li:last', an[i]).removeClass('disabled');
				}
			}
		}
	}
});

/* ---------- Page width functions ---------- */

$(window).bind("resize", widthFunctions);

function widthFunctions(e) {
	
    var winHeight = $(window).height();
    var winWidth = $(window).width();

	var contentHeight = $("#content").height();

	if (winHeight) {
		
		$("#content").css("min-height",winHeight);
		
	}
	
	if (contentHeight) {
		
		$("#sidebar-left2").css("height",contentHeight);
		
	}
    
	if (winWidth < 980 && winWidth > 750) {
		
		if($("#sidebar-left").hasClass("span2")) {
			
			$("#sidebar-left").removeClass("span2");
			$("#sidebar-left").addClass("span1");
			
		}
		
		if($("#content").hasClass("span10")) {
			
			$("#content").removeClass("span10");
			$("#content").addClass("span11");
			
		}
		
		
		$("a").each(function(){
			
			if($(this).hasClass("quick-button-small span1")) {

				$(this).removeClass("quick-button-small span1");
				$(this).addClass("quick-button span2 changed");
			
			}
			
		});
		
		$(".circleStatsItem, .circleStatsItemBox").each(function() {
			
			var getOnTablet = $(this).parent().attr('onTablet');
			var getOnDesktop = $(this).parent().attr('onDesktop');
			
			if (getOnTablet) {
			
				$(this).parent().removeClass(getOnDesktop);
				$(this).parent().addClass(getOnTablet);
			
			}
			  			
		});
		
		$(".box").each(function(){
			
			var getOnTablet = $(this).attr('onTablet');
			var getOnDesktop = $(this).attr('onDesktop');
			
			if (getOnTablet) {
			
				$(this).removeClass(getOnDesktop);
				$(this).addClass(getOnTablet);
			
			}
			  			
		});
		
		$(".widget").each(function(){
			
			var getOnTablet = $(this).attr('onTablet');
			var getOnDesktop = $(this).attr('onDesktop');
			
			if (getOnTablet) {
			
				$(this).removeClass(getOnDesktop);
				$(this).addClass(getOnTablet);
			
			}
			  			
		});
		
		$(".statbox").each(function(){
			
			var getOnTablet = $(this).attr('onTablet');
			var getOnDesktop = $(this).attr('onDesktop');
			
			if (getOnTablet) {
			
				$(this).removeClass(getOnDesktop);
				$(this).addClass(getOnTablet);
			
			}
			  			
		});
							
	} else {
		
		if($("#sidebar-left").hasClass("span1")) {
			
			$("#sidebar-left").removeClass("span1");
			$("#sidebar-left").addClass("span2");
			
		}
		
		if($("#content").hasClass("span11")) {
			
			$("#content").removeClass("span11");
			$("#content").addClass("span11");
			
		
		}
		
		$("a").each(function(){
			
			if($(this).hasClass("quick-button span2 changed")) {

				$(this).removeClass("quick-button span2 changed");
				$(this).addClass("quick-button-small span1");
			
			}
			
		});
		
		$(".circleStatsItem, .circleStatsItemBox").each(function() {
			
			var getOnTablet = $(this).parent().attr('onTablet');
			var getOnDesktop = $(this).parent().attr('onDesktop');
			
			if (getOnTablet) {
			
				$(this).parent().removeClass(getOnTablet);
				$(this).parent().addClass(getOnDesktop);
			
			}
			  			
		});
		
		$(".box").each(function(){
			
			var getOnTablet = $(this).attr('onTablet');
			var getOnDesktop = $(this).attr('onDesktop');
			
			if (getOnTablet) {
			
				$(this).removeClass(getOnTablet);
				$(this).addClass(getOnDesktop);
			
			}
			  			
		});
		
		$(".widget").each(function(){
			
			var getOnTablet = $(this).attr('onTablet');
			var getOnDesktop = $(this).attr('onDesktop');
			
			if (getOnTablet) {
			
				$(this).removeClass(getOnTablet);
				$(this).addClass(getOnDesktop);
			
			}
			  			
		});
		
		$(".statbox").each(function(){
			
			var getOnTablet = $(this).attr('onTablet');
			var getOnDesktop = $(this).attr('onDesktop');
			
			if (getOnTablet) {
			
				$(this).removeClass(getOnTablet);
				$(this).addClass(getOnDesktop);
			
			}
			  			
		});
		
	}
	
	if($('.timeline')) {
		
		$('.timeslot').each(function(){
			
			var timeslotHeight = $(this).find('.task').outerHeight();
			
			$(this).css('height',timeslotHeight);
			
		});
		
	}

}

/******************************************* For Login Page ************************************************/
	$("#loginForm").submit(function(event) {
		event.preventDefault();
		var user = document.forms["loginForm"]["username"].value;
		var pass = document.forms["loginForm"]["password"].value;
		$.ajax({
			type: "post",
			data: {username:user, password:pass, csrfmiddlewaretoken: getCookie('csrftoken')},
			cache: false,
			url: BASE_URL + "login/",
			dataType: "text",
			error: function (xhr, status, error) {
				Done();
				$( "#messageParagraph" ).css( "color", "red" );
				$('#messageParagraph').text(xhr.responseText);

			},
			success: function (user_type) {
				$('#messageParagraph').text('');
				window.location.replace(SERVER_URL + next_redirect_url);
			}
		});
	});


/**************************** For Password Forget Page **************************************/
	$("#forgetForm").submit(function(event) {
		event.preventDefault();
		var user = document.forms["forgetForm"]["username"].value;
		Loading();
		$.ajax({
			type: "post",
			data: {username:user, csrfmiddlewaretoken: getCookie('csrftoken')},
			cache: false,
			url: BASE_URL + "account/passforgot/",
			dataType: "text",
			error: function (xhr, status, error) {
				Done();
				$( "#usercheckmessage" ).css( "color", "red" );
				$('#usercheckmessage').text(xhr.responseText);
			},
			success: function (response) {
				Done();
				$( "#usercheckmessage" ).css( "color", "green" );
				$('#usercheckmessage').text(response);
				setTimeout(function(){ window.location = BASE_URL + "login/"; }, 4000);
			}
		});
	});

/*************************** For Registration Page  ********************************************/
	$("#registerForm").submit(function(event) {
		Loading();
		event.preventDefault();
		var data = {username: document.forms["registerForm"]["username"].value,
					password: document.forms["registerForm"]["password"].value,
					firstname: document.forms["registerForm"]["firstname"].value,
					lastname: document.forms["registerForm"]["lastname"].value,
					birthday: document.forms["registerForm"]["birthday"].value,
					gender: document.forms["registerForm"]["gender"].value,
					email: document.forms["registerForm"]["email"].value,
					csrfmiddlewaretoken: getCookie('csrftoken')
		};
		$( "#usernamemessage").addClass('hidden');
		$( "#birthdaymessage").addClass('hidden');
		$( "#emailmessage").addClass('hidden');
		$.ajax({
			type: "post",
			data: data,
			cache: false,
			url: BASE_URL + "account/register/",
			dataType: "text",
			error: function (xhr, status, error) {
				Done();
				var response = xhr.responseText;
				if (response == "UsernameExists") {
					$("#usernamemessage").removeClass('hidden');
				}
				else if (response == "EmailExists") {
					$("#emailmessage").removeClass('hidden');
				}
				else if (response == "BirthdayError") {
					$("#birthdaymessage").removeClass('hidden');
				}
				else {
					alert('Some fields have not been filled')
				}
			},
			success: function (response) {
				Done();
				$('#registermessage').text(response);
				setTimeout(function(){ window.location = BASE_URL + 'login' }, 5500);
			}
		});
	});

	$("#passwordResetForm").submit(function(event) {
		event.preventDefault();
		var password = document.forms["passwordResetForm"]["password"].value;
		var repeated_password = document.forms["passwordResetForm"]["repeat_password"].value;
		Loading();
		$.ajax({
			type: "post",
			data: {password:password, repeated_password:repeated_password, csrfmiddlewaretoken: getCookie('csrftoken')},
			cache: false,
			url: window.location.href,
			dataType: "text",
			error: function (xhr, status, error) {
				Done();
				$( "#responseMessage" ).css( "color", "red" );
				$('#responseMessage').text(xhr.responseText);
			},
			success: function (response) {
				Done();
				$( "#responseMessage" ).css( "color", "green" );
				$('#responseMessage').text(response);
				setTimeout(function(){ window.location = BASE_URL + "login/"; }, 4000);
			}
		});
	});