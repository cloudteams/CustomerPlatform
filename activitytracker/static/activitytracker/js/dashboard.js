/**
 * Created by Aggelos on 10/23/2015.
 */

function circle_progess() {

	var divElement = $('div'); //log all div elements

    $(".whiteCircle").knob({
        'min':0,
        'max':100,
        'readOnly': true,
        'width': 120,
        'height': 120,
        'bgColor': 'rgba(255,255,255,0.5)',
        'fgColor': 'rgba(255,255,255,0.9)',
        'dynamicDraw': true,
        'thickness': 0.2,
        'tickColorizeValues': true
    });


	$(".circleStatsItemBox").each(function(){

		var value = $(this).find(".value > .number").html();
		var unit = $(this).find(".value > .unit").html();
		var percent = $(this).find("input").val()/100;

		countSpeed = 2300*percent;

		endValue = value*percent;

		$(this).find(".count > .unit").html(unit);
		$(this).find(".count > .number").countTo({

			from: 0,
		    to: endValue,
		    speed: countSpeed,
		    refreshInterval: 50

		});

		//$(this).find(".count").html(value*percent + unit);

	});

}