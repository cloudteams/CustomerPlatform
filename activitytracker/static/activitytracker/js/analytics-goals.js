/**
 * Created by Aggelos.
 */
var svg = dimple.newSvg(".analytics-topChart", "100%", 500);
    var svg2 = dimple.newSvg(".analytics-bottomChart", "100%", 600);
    var svg3 = dimple.newSvg(".analytics-extraChart", "100%", 600);

    $('select[name="analysis-select"], #dateRange, select[name="activity-select"], #allActivitiesChecked').on('change', function(){
        if ($("#allActivitiesChecked").prop('checked')) {
            $('#activity-select').prop('disabled', true).trigger("liszt:updated");
            ActivityGoalsDonutChart('all');
        }
        else    {
            $('#activity-select').prop('disabled', false).trigger("liszt:updated");
            ActivityGoalsDonutChart($('#activity-select').val());
        }

        if ($('#analysis-select').val() == "Activities & Categories") {
            ActivityAndCategoryGoalsBarChart();
            updateGoalsBanner("Activities & Categories");
        }
        else if ($('#analysis-select').val() == "Activity/Object") {
            ActivityAndObjectGoalsBubbleChart();
            updateGoalsBanner("Activity/Object");
        }
        else {
            ActivityAndFriendGoalsBubbleChart();
            updateGoalsBanner("Activity/Friend");
        }
    });

    function ActivityAndCategoryGoalsBarChart() {
        var range = $('#dateRange').val();
        $('.analytics-bottomChart h1').text('Goal Breakdown for Activities');
        $('.analytics-extraChart h1').text('Goal Breakdown for Categories');
		$.ajax({
			type: "post",
			data: { csrfmiddlewaretoken: getCookie('csrftoken'), range: range},
			cache: false,
			url: BASE_URL + 'analytics/goals/update/categories_activities/',
			dataType: "json",
			error: function (xhr, status, error) {
				Done();
				console.log('went bad');
			},
			success: function (response) {
                try {
                    svg2.selectAll('*').remove();
                    svg3.selectAll('*').remove();
                }
                catch(err) {}
                // Chart for Activities
				var barChartActivities = new dimple.chart(svg2, response[0]);
                barChartActivities.setMargins("60px", "30px", "110px", "70px");
				barChartActivities.setBounds(75, 30, 485, 330);
                var x = barChartActivities.addCategoryAxis("x", "Activity");
                x.addOrderRule("Instances", true);
                x.title = "Activities Breakdown in desc order of Instances";
                barChartActivities.addMeasureAxis("y", "Instances");
                barChartActivities.addLegend("5%", 0, "85%", 20, "right");
				barChartActivities.addSeries("Goal Status", dimple.plot.bar);
                barChartActivities.assignColor("Reached", "green");
                barChartActivities.assignColor("Failed", "rgb(176, 6, 6)");
                barChartActivities.assignColor("In Progress","rgb(255, 203, 0)");
                barChartActivities.assignColor("No Goal set","rgb(235, 235, 236)");
                barChartActivities.width = $('.analytics-bottomChart').width()- 100;
                barChartActivities.draw();

                // Same Chart but for Categories
                var barChartCategories = new dimple.chart(svg3, response[1]);
                barChartCategories.setMargins("60px", "30px", "110px", "70px");
				barChartCategories.setBounds(75, 30, 485, 330);
                x = barChartCategories.addCategoryAxis("x", "Category");
                x.addOrderRule("Instances", true);
                x.title = "Category Breakdown in desc order of Instances";
                barChartCategories.addMeasureAxis("y", "Instances");
                barChartCategories.addLegend("5%", 0, "85%", 20, "right");
				barChartCategories.addSeries("Goal Status", dimple.plot.bar);
                barChartCategories.assignColor("Reached", "green");
                barChartCategories.assignColor("Failed", "rgb(176, 6, 6)");
                barChartCategories.assignColor("In Progress","rgb(255, 203, 0)");
                barChartCategories.assignColor("No Goal set","rgb(235, 235, 236)");
                barChartCategories.width = $('.analytics-extraChart').width()- 100;
                barChartCategories.draw();

                $(window).on('resize', function() {
                    barChartActivities.width = $('.analytics-bottomChart').width() - 100;
                    barChartCategories.width = $('.analytics-bottomChart').width() - 100;
                    barChartActivities.draw(0, true);
                    barChartCategories.draw(0, true);
                });

			}
	    });
     };

 /**************************************************************************************/
    function ActivityGoalsDonutChart(activity_chosen) {
        var range = $('#dateRange').val();
        $('.analytics-topChart h1').text('Goal Status Breakdown');
		$.ajax({
			type: "post",
			data: {activity: activity_chosen, csrfmiddlewaretoken: getCookie('csrftoken'), range: range},
			cache: false,
			url: BASE_URL + 'analytics/goals/update/activity/',
			dataType: "json",
			error: function (xhr, status, error) {
				Done();
				console.log('went bad');
			},
			success: function (response) {
                try {
                    svg.selectAll('*').remove();
                }
                catch(err) {}
                var donutChart = new dimple.chart(svg, response);
                donutChart.setBounds(60, 20, 460, 360);
                donutChart.addMeasureAxis("p", "Instances");
                donutChart.addLegend("82%", 20, 90, 300, "left");
                var outerRing = donutChart.addSeries("Goal Status", dimple.plot.pie);
                donutChart.assignColor("Reached", "green");
                donutChart.assignColor("Failed", "rgb(176, 6, 6)");
                donutChart.assignColor("In Progress","rgb(255, 203, 0)");
                donutChart.assignColor("No Goal set","rgb(235, 235, 236)");
				outerRing.innerRadius = "-30px";

                donutChart.width = $('.analytics-topChart').width()- 100;
                donutChart.draw();

                $(window).on('resize', function() {
                    donutChart.width  = $('.analytics-topChart').width() - 100 ;//- 85;
                    donutChart.draw(0, true);
                });
			}
	    });
    };


 /**************************************************************************************/
    function ActivityAndObjectGoalsBubbleChart() {
        Loading();
        var range = $('#dateRange').val();
        $('.analytics-bottomChart h1').text('Activity to Object Goal Breakdown');
        $('.analytics-extraChart h1').text('');
		$.ajax({
			type: "post",
			data: { csrfmiddlewaretoken: getCookie('csrftoken'), range: range},
			cache: false,
			url: BASE_URL + 'analytics/goals/update/activities_objects/',
			dataType: "json",
			error: function (xhr, status, error) {
				Done();
				console.log('went bad');
			},
			success: function (response) {
                try {
                    svg2.selectAll('*').remove();
                    svg3.selectAll('*').remove();
                }
                catch(err) {}

                var bubbleChart = new dimple.chart(svg2, response);
                bubbleChart.setBounds(95, 25, 575, 575);
                var x = bubbleChart.addCategoryAxis("x", "Object");
                var y = bubbleChart.addCategoryAxis("y", "Activity");
                bubbleChart.addMeasureAxis("p", "Instances");
                var bubbleSeries = bubbleChart.addSeries("Goal Status", dimple.plot.pie);
                var radius_data = maxAxisCategoriesObjects(response);
                var width  = $('.analytics-bottomChart').width() - 100 ;//- 85;
                if (radius_data.axis == "y") {
                    bubbleSeries.outerRadius = Math.round(500.0 / (radius_data.categories * 2)).toString();
                    bubbleSeries.innerRadius = Math.round(500.0 / (radius_data.categories * 4)).toString();
                }
                else {
                    bubbleSeries.outerRadius = Math.round(0.95*width / (radius_data.categories * 2)).toString();
                    bubbleSeries.innerRadius = Math.round(0.95*width / (radius_data.categories* 4)).toString();
                }
                bubbleChart.assignColor("Reached", "green");
                bubbleChart.assignColor("Failed", "rgb(176, 6, 6)");
                bubbleChart.assignColor("In Progress","rgb(255, 203, 0)");
                bubbleChart.assignColor("No Goal set","rgb(235, 235, 236)");
                bubbleChart.width = width;
                x.showGridlines = true;
                y.showGridlines = true;
                Done();
                bubbleChart.addLegend("5%", 0, "85%", 20, "right");
                bubbleChart.draw();


                $(window).on('resize', function() {
                    var new_width  = $('.analytics-bottomChart').width() - 100 ;//- 85;
                    bubbleChart.width = new_width;
                    if (radius_data.axis == "x") {
                        bubbleSeries.outerRadius = Math.round(0.95*new_width / (radius_data.categories * 2)).toString();
                        bubbleSeries.innerRadius = Math.round(0.95*new_width / (radius_data.categories* 4)).toString();
                    }
                    bubbleChart.draw(0, true);
                });
			}
	    });
    };

    /**************************************************************************************/
    function ActivityAndFriendGoalsBubbleChart() {
        Loading();
        var range = $('#dateRange').val();
        $('.analytics-bottomChart h1').text('Activity to Friend Goal Breakdown');
        $('.analytics-extraChart h1').text('');
		$.ajax({
			type: "post",
			data: { csrfmiddlewaretoken: getCookie('csrftoken'), range: range},
			cache: false,
			url: BASE_URL + 'analytics/goals/update/activities_friends/',
			dataType: "json",
			error: function (xhr, status, error) {
				Done();
				console.log('went bad');
			},
			success: function (response) {
                try {
                    svg2.selectAll('*').remove();
                    svg3.selectAll('*').remove();
                }
                catch(err) {}

                var bubbleChart = new dimple.chart(svg2, response);
                bubbleChart.setBounds(95, 25, 575, 575);
                var x = bubbleChart.addCategoryAxis("x", "Friend");
                var y = bubbleChart.addCategoryAxis("y", "Activity");
                bubbleChart.addMeasureAxis("p", "Instances");
                var bubbleSeries = bubbleChart.addSeries("Goal Status", dimple.plot.pie);
                var radius_data = maxAxisCategoriesFriends(response);
                var width  = $('.analytics-bottomChart').width() - 100 ;//- 85;
                if (radius_data.axis == "y") {
                    bubbleSeries.outerRadius = Math.round(500.0 / (radius_data.categories * 2)).toString();
                    bubbleSeries.innerRadius = Math.round(500.0 / (radius_data.categories * 4)).toString();
                }
                else {
                    bubbleSeries.outerRadius = Math.round(0.95*width / (radius_data.categories * 2)).toString();
                    bubbleSeries.innerRadius = Math.round(0.95*width / (radius_data.categories* 4)).toString();
                }
                bubbleChart.assignColor("Reached", "green");
                bubbleChart.assignColor("Failed", "rgb(176, 6, 6)");
                bubbleChart.assignColor("In Progress","rgb(255, 203, 0)");
                bubbleChart.assignColor("No Goal set","rgb(235, 235, 236)");
                bubbleChart.width = width;
                x.showGridlines = true;
                y.showGridlines = true;
                Done();
                bubbleChart.addLegend("5%", 0, "85%", 20, "right");
                bubbleChart.draw();


                $(window).on('resize', function() {
                    var new_width  = $('.analytics-bottomChart').width() - 100 ;//- 85;
                    bubbleChart.width = new_width;
                    if (radius_data.axis == "x") {
                        bubbleSeries.outerRadius = Math.round(0.95*new_width / (radius_data.categories * 2)).toString();
                        bubbleSeries.innerRadius = Math.round(0.95*new_width / (radius_data.categories* 4)).toString();
                    }
                    bubbleChart.draw(0, true);
                });


			}
	    });
    };


    function updateGoalsBanner(analysis_selected) {
        var range = $('#dateRange').val();
        $.ajax({
            type: "post",
            data: {range: range, csrfmiddlewaretoken: getCookie('csrftoken'), analysis:analysis_selected},
            cache: false,
            url: BASE_URL + 'analytics/goals/update/goals_chartbanner/',
            dataType: "json",
            error: function (xhr, status, error) {
                Done();
                console.log('went bad');
            },
            success: function (response) {
                $('#totalActivities').text(response.total_activities);
                $('#totalGoalsSet').text(response.total_goals_set);
                $('#totalPercentageReached').text(response.percentage_of_goals_reached.toFixed(1) + "%");
                $('#date-range-total-analytics').text(range);

                if (analysis_selected == "Activities & Categories") {
                    $('#totalGoalsSetLabel').text("Total Goals set:");
                    $('#totalPercentageReachedLabel').text("Total Goals Reached:");
                }
                else if (analysis_selected == "Activity/Object") {
                    $('#totalGoalsSetLabel').text("Total Goals set using Objects:");
                    $('#totalPercentageReachedLabel').text("Goals Reached using Objects:");
                }
                else {
                    $('#totalGoalsSetLabel').text("Total Goals set with Friends:");
                    $('#totalPercentageReachedLabel').text("Goals Reached with Friends:");
                }
            }
        });
    }

     function maxAxisCategoriesObjects(json_data){
        var hash_activities = {};
        var unique_activities = 0;
        var hash_objects = {};
        var unique_objects = 0;
        $.each(json_data, function(i, e) {
            if (hash_activities[e.Activity] == 1) {}
            else {
               hash_activities[e.Activity] = 1;
               unique_activities += 1;
            }
            if (hash_objects[e.Object] == 1) {}
               else {
                   hash_objects[e.Object] = 1;
                   unique_objects += 1;
               }
        });
        if  (unique_activities > unique_objects) {
            return {'axis':'y', 'categories':unique_activities}
        }
        else {
            return {'axis':'x', 'categories':unique_objects}
        }
     }

     function maxAxisCategoriesFriends(json_data){
        var hash_activities = {};
        var unique_activities = 0;
        var hash_friends = {};
        var unique_friends = 0;
        $.each(json_data, function(i, e) {
            if (hash_activities[e.Activity] == 1) {}
            else {
               hash_activities[e.Activity] = 1;
               unique_activities += 1;
            }
            if (hash_friends[e.Friend] == 1) {}
               else {
                   hash_friends[e.Friend] = 1;
                   unique_friends += 1;
               }
        });
        if  (unique_activities > unique_friends) {
            return {'axis':'y', 'categories':unique_activities}
        }
        else {
            return {'axis':'x', 'categories':unique_friends}
        }
     }


    $('#dateRange').val('01/01/2015 - ' + moment().format("MM/DD/YYYY"));
	$('#dateRange').daterangepicker({
		format: 'MM/DD/YYYY',
		startDate: moment().subtract(1, 'month'),
		endDate: moment(),
		/*sshowDropdowns: true,*/
		ranges: {
		   'Today': [moment(), moment()],
		   'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
		   'Previous Week (Mo-Su)': [moment().subtract(1, 'week').startOf('week').add(1,'day'), moment().subtract(1,'week').endOf('week').add(1,'day')],
		   'Previous Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')],
           'Month to Date': [moment().startOf('month'), moment()],
           'Year to Date': [moment().startOf('year'), moment()]
		},
		locale: {
			monthNames: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
			fromLabel: 'From',
			toLabel: 'To',
			customRangeLabel: 'Calendar Custom Range'
		}
	});


    $(window).on('load', function(){
        $('#dateRange').trigger('change');
    });