/**
 * Created by Aggelos on 9/1/2015.
 */

var svg = dimple.newSvg(".analytics-topChart", "100%", 650);
//var svg2 = dimple.newSvg(".analytics-bottomChart", "100%", 600);

    $('input[name="daytype"],  #dateRange').on('change', function(){
        updateRoutineCharts()
    });

    function updateRoutineCharts() {

        var range = $('#dateRange').val();
        var metric = $('input[name="metric"]:checked').val();
        var day_type = $('input[name="daytype"]:checked').val();
        var routineChecked = $('input[name="routine-radiobutton"]:checked').val();

        $('.analytics-topChart h1').text('Routine Action Distribution');
       // $('.analytics-bottomChart h1').text('Activity Metric Categorization');

		$.ajax({
			type: "post",
			data: {
                csrfmiddlewaretoken: getCookie('csrftoken'),
                range: range,
                routine: routineChecked,
                day_type:day_type
            },
			cache: false,
			url: BASE_URL + "analytics/routine/update/activities_all/",
			dataType: "json",
			error: function (xhr, status, error) {
				console.log('went bad');
			},
			success: function (response) {
                console.log(response);
                try {
                    svg.selectAll('*').remove();
                   // svg2.selectAll('*').remove();
                }
                catch(err) {}

                var barChart = new dimple.chart(svg, response);

                barChart.setBounds(75, 30, 485, 330);
                barChart.setMargins("60px", "30px", "110px", "70px");

                barChart.defaultColors = [
                    new dimple.color("#106D1B"), new dimple.color("#8A0505"),
                    new dimple.color("#7b6888"), new dimple.color("#E07C27"),
                    new dimple.color("#a05d56"), new dimple.color("#d0743c"),
                    new dimple.color("#7b6888"), new dimple.color("#266419")
                ];

                var y = barChart.addCategoryAxis("y", "Action");
                var x = barChart.addMeasureAxis("x", "Hours");

                x.showGridlines = true;
                x.tickFormat = ',.2f';
                y.addOrderRule("OrderByTime", false);
                y.title = "Actions in desc order of Metric";

                var series = barChart.addSeries("Timeslice", dimple.plot.bar);
                series.addOrderRule('Timeslice', true);
                barChart.addLegend(60, 10, 510, 20, "right");
                barChart.width = $('.analytics-bottomChart').width()- 100;
                barChart.draw();



                $('input[name="metric"]').on('change', function() {
					var metric = $('input[name="metric"]:checked').val();
					if ( metric == "instances") {

                        x.measure = "Instances";
                        x.tickFormat = '';
                        y._orderRules[0].ordering = "OrderByInstances";
					}
					else{

                        x.measure = "Hours";
                        x.tickFormat = ',.2f';
                        y._orderRules[0].ordering = "OrderByTime";
					}
                    barChart.draw();
    			});

                $(window).on('resize', function() {
                    barChart.width = $('.analytics-bottomChart').width() - 100;
                    barChart.draw(0, true);
                });
			}
	    });
     };


 /**************************************************************************************/

    function updateActivitiesBanner(activity_selected) {
        var range = $('#dateRange').val();
        $.ajax({
            type: "post",
            data: {range: range, csrfmiddlewaretoken: getCookie('csrftoken'), activity: activity_selected},
            cache: false,
            url: BASE_URL + "analytics/activities/update/activities_chartbanner/",
            dataType: "json",
            error: function (xhr, status, error) {
                Done();
                console.log('went bad');
            },
            success: function (response) {
                $('#totalActivities').text(response.total_activities);
                $('#extraMutableAnalytic').text(response.extra_mutable_analytic.toFixed(1) + "%");
                $('#totalTimeSpent').text(response.total_time_spent);
                $('#date-range-total-analytics').text(range);

                if (activity_selected == "all") {
                    $('#totalActivitiesLabel').text("Total Activities performed:");
                    $('#extraMutableAnalyticLabel').text("Percentage of unique Activities:");
                    $('#totalTimeSpentLabel').text("Total Time spent on Activities:");
                }
                else {
                    $('#totalActivitiesLabel').text("Total Instances of Activity:");
                    $('#extraMutableAnalyticLabel').text("Presence in it's Category:");
                    $('#totalTimeSpentLabel').text("Time spent on this Activity:");
                }
            }
        });
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
        $.ajax({
            type: "get",
            url: BASE_URL + 'account/routine',
            dataType: "json",
            error: function (xhr, status, error) {
                alert("Error occured, try again")
            },
            success: function (responseJSON) {

                var container = $('#routine-activity-list');

                $.each(responseJSON['input_data'], function (i, e) {

                    var innerContainer = document.createElement('div');
                    $(innerContainer).css('width', '60px');
                    $(innerContainer).css('margin-right', '28px');
                    var routine_activity = document.createElement("a");
                    routine_activity.className = 'quick-button metro circle routine ' + e.color;
                    $(routine_activity).attr('title', e.activity);

                    var icon = document.createElement("i");
                    icon.className = 'activicon-' + e.icon_classname;

                    routine_activity.appendChild(icon);

                    var rdio = document.createElement('input');
                    rdio.className = 'routine-radiobutton';
                    rdio.id = e.activity.replace(/ /g, '-');
                    rdio.type = 'radio';
                    rdio.name = 'routine-radiobutton';
                    $(rdio).css('height', '15px');
                    $(rdio).css('width', '20px');
                    $(rdio).css('margin-top', '8px');
                    $(rdio).css('margin-left', '22px');
                    $(rdio).prop('value', rdio.id);
                    $(innerContainer).append(routine_activity);
                    $(innerContainer).append(rdio);


                    $(container).append(innerContainer);
                });
                $('.routine-radiobutton').on('change', function(){
                    updateRoutineCharts();
                });
                $('.routine').on('click', function() {
                    var corresponding_radio_id = $(this).closest('div').find('input').prop('id');
                    $('#' +corresponding_radio_id).prop('checked',true);
                    $('#' +corresponding_radio_id).trigger('change')
                });

                $('#Working').prop('checked', true);
                $('#Working').trigger('change');
            }
        })
    });

    function sortByKey(array, key) {
        return array.sort(function(a, b) {
            var x = a[key];
            var y = b[key];
            return ((x > y) ? -1 : ((x < y) ? 1 : 0));
        });
    }
    function sortReverseByKey(array, key) {
        return array.sort(function(a, b) {
            var x = a[key];
            var y = b[key];
            return ((x < y) ? -1 : ((x > y) ? 1 : 0));
        });
    }

