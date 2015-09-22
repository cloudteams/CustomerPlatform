/**
 * Created by Aggelos on 9/1/2015.
 */

var svg = dimple.newSvg(".analytics-topChart", "100%", 650);

    $('input[name="daytype"],  #dateRange').on('change', function(){
        updateRoutineCharts()
    });

    function updateRoutineCharts() {

        var range = $('#dateRange').val();
        var metric = $('input[name="metric"]:checked').val();
        var day_type = $('input[name="daytype"]:checked').val();
        var routineChecked = $('input[name="routine-radiobutton"]:checked').val();

        $('.analytics-topChart h1').text('Routine Action Distribution');

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
				console.log('Oh oh, something went bad');
			},
			success: function (response) {
                try {
                    svg.selectAll('*').remove();
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
                updateRoutineBanner(response);



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

    function updateRoutineBanner(response) {

        var total_time = 0;
        var shared_time = 0;

        $.each(response, function(i, object) {
            if (object['Timeslice'] == "Routine Metric Overlap" ) {
                shared_time += object['Hours']
            }
            total_time += object['Hours']
        });

        var shared_duration_percentage = ((shared_time/total_time) * 100).toFixed(2);

        $('#date-range-total-analytics').text($('#dateRange').val());

        $('#totalActions').text(response.length);
        $('#actionOverlapPercentage').text(shared_duration_percentage + '%');
        $('#totalTimeShared').text(shared_time.toFixed(2));
    }

    /******************************************************************************/

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
        updateRoutineCharts()
    });
