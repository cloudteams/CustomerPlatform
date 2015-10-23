/**
 * Created by Aggelos on 10/23/2015.
 */

$(document).on('ready',function(){

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
		var percent = $(this).find("input").val()/100;

        (percent == 0) ? CountSpeed = 1 : countSpeed = 3000*percent;

		endValue = $(this).find(".count > .number").html();

		$(this).find(".count > .number").countTo({

			from: 0,
		    to: endValue,
		    speed: countSpeed,
		    refreshInterval: 50

		});

	});

});

function updateSingleActivityCharts() {
    var range = $('#dateRange').val();
    var metric = $('#metric-select').val();
    $('.analytics-bottomChart h1').text('Instance Tracking');
    $('.analytics-topChart h1').text('Day to Day Analysis');
    $.ajax({
        type: "post",
        data: {activity: activity_chosen, csrfmiddlewaretoken: getCookie('csrftoken'), range: range},
        cache: false,
        url: BASE_URL + "analytics/activities/update/activities_single/",
        dataType: "json",
        error: function (xhr, status, error) {
            Done();
            console.log('went bad');
        },
        success: function (response) {
            try {
                svg.selectAll('*').remove();
                svg2.selectAll('*').remove();
            }
            catch(err) {}
            var timelineChart = new dimple.chart(svg, response[0]);
            timelineChart.setBounds(60, 30, 505, 305);


            var x = timelineChart.addTimeAxis("x", "Date", "%m/%d/%Y", findProperInterval(range)[1]);
            x.timeInterval = 1;
            if (findProperInterval(range)[0] == "days") {
                x.timePeriod = d3.time.days
            }
            else if (findProperInterval(range)[0] == "weeks") {
                x.timePeriod = d3.time.weeks
            }
            else {
                x.timePeriod = d3.time.months
            }

            if (metric == "Number of Instances") {
                var y = timelineChart.addMeasureAxis("y", "Instances");
            }
            else {
                var y = timelineChart.addMeasureAxis("y", "Hours");
            }

            var category_color_dict = {"Communication/Socializing": "blue",
                                       "Fun/Leisure/Hobbies": "orange",
                                       "Responsibilities": "rgb(94, 18, 4)",
                                       "Self-care/Everyday Needs": "rgb(56, 60, 55)",
                                       "Transportation": "purple",
                                       "Sports/Fitness": "rgb(129, 189, 116)"
            };
            for (var key in category_color_dict) {
                timelineChart.assignColor(key, category_color_dict[key]);
            }
            timelineChart.defaultColors = [new dimple.color("#25333E")];
            var s = timelineChart.addSeries("Series", dimple.plot.line);
            timelineChart.addLegend("5%", 10, "85%", 20, "right");
            s.interpolation = "step";
            timelineChart.width  = $('.analytics-topChart').width() - 100 ;
            timelineChart.draw();



            /* Definitions of lineChart that will be the 2nd chart for single activities */
            var color_dict = {'0': "#C0BBBB", '1': "red", '2': "yellow", '3': "green"};
            var goal_dict = {'0': "n/a", '1': "Failed", '2': "In Progress", '3': "Reached"};
            var lineChart = new dimple.chart(svg2, response[1]);
            lineChart.setBounds(60, 30, 530, 305);
            lineChart.addMeasureAxis("y", "Hours");

            var linechart_x = lineChart.addCategoryAxis("x", "Start_Date");
            linechart_x.addOrderRule("Timeorder");
            linechart_x.title = "Instances ordered by Date";
            if ((response[1].length > 1) && (!AllSameStatus(response[1]))) {
                var goal_status_prices_exist = {"0": 0, "1": 0, "2": 0, "3":0 };
                var goal_status_color_list = [];
                $.each(response[1], function(i, e) {
                       goal_status_prices_exist[e.Goal_Status.toString()] = 1;
                });
                if (goal_status_prices_exist["0"] == 1)
                    goal_status_color_list.push("#C0BBBB");
                if (goal_status_prices_exist["1"] == 1)
                    goal_status_color_list.push("red");
                if (goal_status_prices_exist["2"] == 1)
                    goal_status_color_list.push("yellow");
                if (goal_status_prices_exist["3"] == 1)
                    goal_status_color_list.push("green");

                lineChart.addColorAxis("Goal_Status", goal_status_color_list);
                var lines = lineChart.addSeries(null, dimple.plot.line);
            }
            else {
                var lines = lineChart.addSeries("Line", dimple.plot.line);
                if (response[1].length > 0) {
                    lineChart.assignColor('Line', color_dict[response[1][0].Goal_Status])
                }
            }
            lines.lineWeight = 5;
            lines.lineMarkers = true;
            lines.getTooltipText = function (e) {
               if (response[1].length == 1) {
                   e.cValue = response[1][0].Goal_Status;
               }
               return ["Date Started: " + e.x, "Hours: " + e.yValue, "Goal: " + goal_dict[e.cValue]]
            };

            lineChart.width = $('.analytics-bottomChart').width()- 100;
            lineChart.draw();

            function AllSameStatus(list){
                var flag = true;
                try {
                    var status = list[0].Goal_Status
                }
                catch(err) {
                    return true;
                }
                $.each(list, function(i, e) {
                    if (e.Goal_Status != status) {
                        flag = false;
                    }
                });
                if (flag) {
                    return true;
                }
                else {
                    return false;
                }
            };

            function findProperInterval(range) {
                var string_startDate = range.split("-")[0].replace(" ","");
                var string_endDate = range.split("-")[1].replace(" ","");
                var moment_start = moment(string_startDate, "MM/DD/YYYY");
                var moment_end = moment(string_endDate, "MM/DD/YYYY");
                var gap = moment_end.diff(moment_start,"days");
                if (gap <= 14) {
                    return ["days","%d %b %Y"]
                }
                else if (gap <= 90) {
                    return ["weeks","%d %b %Y"]
                }
                else {
                    return ["months","%b %Y"]
                }
            };



            $('select[name="metric-select"]').off().on('change', function() {
                metric = $('#metric-select').val();
                if (metric == "Number of Instances") {
                    y.measure = "Instances"
                }
                else {
                    y.measure = "Hours"
                }
                timelineChart.draw();
            });

            $(window).on('resize', function() {
                timelineChart.width  = $('.analytics-topChart').width() - 100 ;
                lineChart.width  = $('.analytics-bottomChart').width() - 100 ;
                lineChart.draw(0, true);
                timelineChart.draw(0, true);
            });


        }
    })
}