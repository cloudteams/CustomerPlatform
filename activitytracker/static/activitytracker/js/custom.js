/*Aggelos Javascript/jQuery */

var SERVER_URL = "";
var BASE_URL =  "/activitytracker/";

function Loading(){
	$("#overlay").show();
}

$('.dropdown').hover(function() {
	  $(this).find('.dropdown-menu').stop(true, true).fadeIn();
	}, function() {
	  $(this).find('.dropdown-menu').stop(true, true).delay(50).fadeOut();
});

$('body').on('hidden.bs.modal', '.modal', function () {
	$(this).removeData('bs.modal');
});


//function CalculateUtcOffset(lat, lng) {
//
//	if ((lat == null) || (lng == null) || (lat == 0) || (lng == 0)){
//		return 0
//	}
//
//	$.ajax({
//		type: "get",
//		url: 'https://maps.googleapis.com/maps/api/timezone/json',
//		data: {location: lat.toString() + ',' + lng.toString(), timestamp: 0},
//		async: false,
//		dataType: "json",
//		success: function (response) {
//			try {
//				utcOffset = (response['rawOffset'] + response['dstOffset'])/ 3600
//			}
//			catch (e) {utcOffset =  0}
//		},
//		error: function(){
//			utcOffset = 0
//		}
//	});
//
//	return utcOffset
//}


function ScriptIsLoaded(scriptTag){
    var scripts = document.getElementsByTagName("script");
	var src;
    for(var i = 0; i < scripts.length; i++) {
		try {
			src = scripts[i].getAttribute('src');
			if (src.indexOf(scriptTag) > -1)
			return true
		}
		catch(err) {}
	}
    return false;
}

function LoadingWithBackdrop(){
	$("#overlay").show();
	$('<div class="modal-backdrop fade in"></div>').appendTo(document.body);
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
				error: function(xhr){
					console.log(xhr.responseText);
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
		 var friends = $('#' + form.toString() + ' input[name=friends]').val().toString();
	 }
	 catch (e){
		var friends = ""
	 }
	 try {
		 var tools = $('#'+ form.toString() +' input[name=tools]').val().toString();
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


function eraseAllActivities(){
	$(".activity-flag").remove();
};

function drawActivity(e) {
	var new_activity = document.createElement("a");
	var classes = 'quick-button metro col-sm-2 activity-flag ' + e.colour;
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

	if ($('.col-xs-12 .col-lg-6 .activity-flag').length < 9) {
		var rows = $('.col-xs-12 .col-lg-6 .row');
		var first_row = rows[0];
		var second_row = rows[1];
		var third_row = rows[2];
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
		new_activity.className = 'quick-button metro col-sm-2 activity-flag ' + e.colour;
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
			divN.className = 'row';
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
			drawDonut();
		}
	});
}

function CalendarDaterange(viewInstance){
	var day,month,year,day2,month2,year2;
	var period = String(viewInstance.title.replace(/[^a-zA-Z0-9, ]/g,"-"));
	var mode = String(viewInstance.name);
	if (mode == "agendaDay"){
		var dateparts = period.split(", ");
		year = dateparts[1];
		month = (dateparts[0].split(" "))[0];
		day = (dateparts[0].split(" "))[1];
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
		if (period.length <= 17){ //same month
			range = period.split("-");
			month = (range[0].split(" "))[0];
			day = (range[0].split(" "))[1];
			day2 = (range[1].replace(',','').split(" "))[1];
			year = (range[1].replace(',','').split(" "))[2];
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
			month2 = (range[1].replace(',','').split(" "))[1];
			day2 = (range[1].replace(',','').split(" "))[2];
			year = year2 = (range[1].replace(',','').split(" "))[3];
			day2 = "0" + day2; // this day would have only 1 digit, due to being between months
			return {mode: mode, day: day, month: month, year: year2, day2: day2, month2: month2, year2: year2}
		}
		else{  // diff months & diff years
			var range = period.split("-");
			month = (range[0].split(" "))[0];
			day = (range[0].split(" "))[1];
			year = (range[0].split(" "))[2];
			month2 = (range[1].replace(',','').split(" "))[1];
			day2 = (range[1].replace(',','').split(" "))[2];
			year2 = (range[1].replace(',','').split(" "))[3];
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
		 },
		 success: function (responseString) {
			 DrawGroupUngroupSortWithChart(responseString);
			 Done();
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


	/* ----------- Show video if not on XS ------------ */
	if ($(window).width() >= 800) {

		$('#videoModal').modal('show');

	}

	$('#videoModal').on('hidden.bs.modal', function () {
        $('#videoModal').remove()
    });

	/* ---------- Acivate Functions ---------- */
	template_functions();
	charts();
	calendars();

});


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
	
	/* ---------- Disable moving to top ---------- */
	$('a[href="#"][data-top!=true]').click(function(e){
		e.preventDefault();
	});
	
	/* ---------- Datepicker ---------- */
	$('.datepicker').datepicker({
		autoclose: true
	});

	/* ---------- Uniform ---------- */
	if (ScriptIsLoaded('uniform')) {
		$("input:checkbox, input:radio, input:file").not('[data-no-uniform="true"],#uniform-is-ajax').uniform();
	}
	/* ---------- Choosen ---------- */
	if (ScriptIsLoaded('chosen')) {
		$('[data-rel="chosen"],[rel="chosen"]').chosen();
	}
	/* ---------- Tabs ---------- */
	$('#myTab a:first').tab('show');
	$('#myTab a').click(function (e) {
	  e.preventDefault();
	  $(this).tab('show');
	});


	/* ---------- Tooltip ---------- */
	$('[rel="tooltip"],[data-rel="tooltip"]').tooltip({"placement":"bottom",delay: { show: 400, hide: 200 }});

	/* ---------- Popover ---------- */
	$('[rel="popover"],[data-rel="popover"]').popover();


	/* ---------- Fullscreen ---------- */


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

		header: {
			left: 'title',
			right: 'prev,next today,month,agendaWeek,agendaDay'
		},
		viewRender: function(view, element) {
			RenderViewActivities(view);
		},
		dayClick: function(date, view) {

			var start_date_default = date.format("MM/DD/YYYY");
			var end_date_default = start_date_default;
			var start_time_default = date.format("HH:mm");

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
		events: BASE_URL + "index/eventstojson/",
		timeFormat: 'H(:mm)'
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

	/* ---------- Device chart ---------- */
	
	var data = [
	{ label: "Desktop",  data: 73},
	{ label: "Mobile",  data: 27}
	];



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
		$('#usercheck-error-message').addClass('hidden');
		$.ajax({
			type: "post",
			data: {username:user, csrfmiddlewaretoken: getCookie('csrftoken')},
			cache: false,
			url: BASE_URL + "account/passforgot/",
			dataType: "text",
			error: function (xhr, status, error) {
				Done();
				$('.error-message').removeClass('hidden')
			},
			success: function (response) {
				Done();
				$( ".success-message" ).removeClass('hidden');
				setTimeout(function(){ window.location = BASE_URL + "login/"; }, 4000);
			}
		});
	});

/*************************** For Registration Page  ********************************************/
	$("#registerForm").submit(function(event) {
		Loading();
		event.preventDefault();
		var data = {
					password: document.forms["registerForm"]["password"].value,
					password_repeat: document.forms["registerForm"]["password_repeat"].value,
					email: document.forms["registerForm"]["email"].value,
					csrfmiddlewaretoken: getCookie('csrftoken')
		};
		$( "#emailmessage").addClass('hidden');
		$("#passwordmessage").addClass('hidden');
		$.ajax({
			type: "post",
			data: data,
			cache: false,
			url: BASE_URL + "account/register/",
			dataType: "text",
			error: function (xhr, status, error) {
				Done();
				var response = xhr.responseText;
				if (response == "EmailExists") {
					$("#emailmessage").removeClass('hidden');
				}
				else if (response == "PasswordMismatch") {
					$("#passwordmessage").removeClass('hidden');
				}
				else {
					alert('Some fields have not been filled')
				}
			},
			success: function (response) {
				Done();
				$('.success-message').removeClass('hidden');
				setTimeout(function(){ window.location = BASE_URL + 'login' }, 5500);
			}
		});
	});

/******************************************************************************************/
 	// For Password Reset

	$("#passwordResetForm").submit(function(event) {
		event.preventDefault();
		var password = document.forms["passwordResetForm"]["password"].value;
		var repeated_password = document.forms["passwordResetForm"]["password_repeat"].value;
		Loading();
		$( ".error-message" ).addClass('hidden');
		$.ajax({
			type: "post",
			data: {password:password, repeated_password:repeated_password, csrfmiddlewaretoken: getCookie('csrftoken')},
			cache: false,
			url: window.location.href,
			dataType: "text",
			error: function (xhr, status, error) {
				Done();
				$( ".error-message" ).removeClass('hidden');
			},
			success: function (responsse) {
				Done();
				$( ".success-message").removeClass('hidden');
				setTimeout(function(){ window.location = BASE_URL + "login/"; }, 4000);
			}
		});
	});
