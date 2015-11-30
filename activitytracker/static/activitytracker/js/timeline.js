/**
 * Created by Aggelos.
 */

function createTimelineInstance(instance, align) {
	var timeslot_canvas = document.createElement('div');
	timeslot_canvas.className = 'timeslot';
	timeslot_canvas.id = "Timeline" + instance.id;
	if (align == "right") {
		timeslot_canvas.className +=' alt'
	}
	var container = document.createElement('div');
	container.className = 'task ';
	var modal_a = document.createElement('a');
	$(modal_a).css('outline','none');
	$(modal_a).attr('data-toggle','modal');
	$(modal_a).attr('data-target','#showActivityModal');
	modal_a.href = '/activitytracker/activity/display-activity/' + instance.id;
	var content = document.createElement('span');
	$(content).addClass('row')
	var activity = jQuery.parseHTML("<span class='timeslot-title col-xs-12'><span class='col-sm-8'>" + instance.activity + "</span><span class='col-sm-4'></span></span>");
	$(content).append(activity);

	if (instance.tools != "") {
		var using = jQuery.parseHTML("<i class='fa fa-wrench timeslot-icon'></i>");
		$(content).find('.timeslot-title span:nth-child(2)').append(using);
	}
	if (instance.location_address != "") {
		var location = jQuery.parseHTML("<i class='fa fa-map-marker timeslot-icon'></i>");
		$(content).find('.timeslot-title span:nth-child(2)').append(location);
	}
	if (instance.result != ""){
		var result = jQuery.parseHTML("<i class='fa fa-ok-circle timeslot-icon'></i>");
		$(content).find('.timeslot-title span:nth-child(2)').append(result);
	}
	if (instance.goal != ""){
		var goal = jQuery.parseHTML("<i class='fa fa-trophy timeslot-icon'></i>");
		$(content).find('.timeslot-title span:nth-child(2)').append(goal);
	}
	if (instance.friends != "") {
		var together_with = jQuery.parseHTML("<i class='fa fa-group timeslot-icon'></i>");
		$(content).find('.timeslot-title span:nth-child(2)').append(together_with);
	}
	var duration = jQuery.parseHTML("<span><i>Duration</i><span class='tl-display'>" + (instance.duration).replace(/([a-z])/g,'$1 ') + "</span></span>");
	$(content).append(duration);

	$(modal_a).append(content);
	$(container).append(modal_a);

	var map_marker = jQuery.parseHTML("<div class='icon " + instance.colour +"'><i class='activicon-" + instance.icon_classname + "'></i></div>");
	var start_time = jQuery.parseHTML("<div class='time'>" + instance.start_date + "</div>");
	$(timeslot_canvas).append(container, map_marker, start_time);
	return timeslot_canvas;
}



function drawTimeline(page) {
	var return_value = 1;
	$.ajax({
		type: "get",
		async: true,
		data: {'page': page, csrfmiddlewaretoken: getCookie('csrftoken')},
		cache: false,
		url: BASE_URL + 'timelinejson/',
		dataType: "json",
		error: function (xhr, status, error) {
			Done();
			alert(xhr.responseText);
		},
		success: function (responseJSON) {
			Loading();
			$.each(responseJSON, function(i, e) {
				if (i%2 == 0){
					$('.timeline').append(createTimelineInstance(e,'left'),"<div class='clearfix'></div>")

				}
				else{
				   $('.timeline').append(createTimelineInstance(e,'right')," <div class='clearfix'></div>")
				}
			});
			Done();
			return_value = responseJSON.length
		}
	});
	return return_value
}

var next_page = (function () {
	var counter = 1;
	return function () {return counter += 1;}
})();


function TimelinePagination() {
	drawTimeline(1);
	var next_page = (function () {
						var counter = 1;
						return function () {return counter += 1;}
					})();

	$(document).scroll(function(e){
		  var scrollAmount = $(window).scrollTop();
		  var documentHeight = $(document).height();
		  var windowHeight = $(window).height();

		  var scrollPercent = (scrollAmount / (documentHeight - windowHeight)) * 100;
		  var roundScroll = Math.round(scrollPercent);


		  if (roundScroll >= 90){
			 if (drawTimeline(next_page()) == 0) {
				$( this ).unbind( e )
			 }
		  }


	});
}

$('#showActivityModal')
	.on("shown.bs.modal", function (e){
		try {
			initializeShowMap();
		}
		catch(err) {}
	});

$('#editActivityModal')
	.on("shown.bs.modal", function (e) {
		try {
			$('body').addClass('modal-open');
			initializeEditMap();
		}
		catch(err) {}
	});


/* Update Activity */
function handleActivityUpdate(update_url) {
	var id_clicked = $('.modal-body-replacement').attr('id');
	var data = submitFields('editForm', getCookie('csrftoken'));
	data.lat = markerEdit.getPosition().lat();
	data.lng = markerEdit.getPosition().lng();
	Loading();
	$.ajax({
		type: "post",
		data: data,
		cache: false,
		url: update_url,
		dataType: "json",
		error: function (xhr, status, error) {
			Done();
			alert(xhr.responseText);
		},
		success: function (response) {
			updateTimelineActivity(response);// update details of activity on the Timeline
			$('#editActivityModal').modal('hide');
			Done();

		}
	});

}

function handleActivityDelete(delete_url){
	Loading();
	$.ajax({
		type: "post",
		data: { csrfmiddlewaretoken: getCookie('csrftoken')},
		cache: false,
		url: delete_url,
		dataType: "text",
		error: function (xhr, status, error) {
			DoneWithBackdrop();
			alert('Something went wrong. Page will be refreshed');
			window.location.reload();
		},
		success: function (response) {
			$('.timeline').empty();
			TimelinePagination();
			$('#showActivityModal').modal('hide');
			Done()

		}
	});

}


function updateTimelineActivity(server_rep) {
	var prev_start_date = $('#Timeline'+ server_rep.id + ' div:nth-child(3)').text();
	if (server_rep.start_date != prev_start_date) {
		$('.timeline').empty();
		TimelinePagination();
		Done();
	}
	else {
		var timeslot = $('#Timeline'+ server_rep.id);
		if ($(timeslot).attr('class').indexOf('alt') == -1) {
			$(timeslot).replaceWith(createTimelineInstance(server_rep,'left'))
		}
		else {
			$(timeslot).replaceWith(createTimelineInstance(server_rep,'right'))
		}
	}
}


TimelinePagination();