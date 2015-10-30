/**
 * Created by Aggelos.
 */

var svg = dimple.newSvg(".analytics-topChart", "100%", 600);
    var svg2 = dimple.newSvg(".analytics-bottomChart", "100%", 600);

    $('select[name="place-select"], #dateRange, #allPlacesChecked').on('change', function(){
        updatePlacesChartsAndBanner();
    });

    function ActivitiesInPlaceDonutChart(place_selected) {
        var range = $('#dateRange').val();
        var metric = $('#metric-select').val();
        var radius = $('#radius-select').data('slider').getValue();
        $('.analytics-topChart h1').text('Category/Activity Distribution');

		$.ajax({
			type: "post",
			data: {place: place_selected, radius: radius, csrfmiddlewaretoken: getCookie('csrftoken'), range: range},
			cache: false,
			url: BASE_URL + 'analytics/places/update/categories_activities/',
			dataType: "json",
			error: function (xhr, status, error) {
				Done();
				console.log('went bad');
			},
			success: function (response) {
                try {
                    svg.selectAll('*').remove();
                    if (place_selected != "all") {
                        $('.analytics-bottomChart h1').text('');
                        svg2.selectAll('*').remove();
                    }
                }
                catch(err) {}
                updateMarkers(response[2], response[3], map);
                var chartOuter = new dimple.chart(svg, response[1]);
                var chartInner = new dimple.chart(svg, response[0]);
                chartOuter.setBounds('5%', '10%', '75%', '80%');
                chartInner.setBounds('5%', '10%', '75%', '80%');

                var inner_p, outer_p;
                if ( metric == "Number of Instances") {
                    outer_p = chartOuter.addMeasureAxis("p", "Instances");
                    inner_p = chartInner.addMeasureAxis("p", "Instances");
				}
                else{
                    outer_p = chartOuter.addMeasureAxis("p", "Hours");
                    inner_p = chartInner.addMeasureAxis("p", "Hours");
                }
				chartOuterLegend = chartOuter.addLegend("82%", 120, 90, 300, "left");
				chartInnerLegend = chartInner.addLegend("82%", 20, 90, 300, "left");
                var outerRing = chartOuter.addSeries("Activity", dimple.plot.pie);
                var innerRing = chartInner.addSeries("Category", dimple.plot.pie);
                outerRing.addOrderRule("Category");
                innerRing.addOrderRule("Category");
				outerRing.innerRadius = "-30px";
				innerRing.outerRadius = "-40px";
				innerRing.innerRadius = "-70px";

				chartOuter.defaultColors = [new dimple.color("#98abc5"), new dimple.color("#8a89a6"), new dimple.color("#ff8c00"),new dimple.color("#995411"),
                                            new dimple.color("#7b6888"), new dimple.color("#E07C27"), new dimple.color("#a05d56"), new dimple.color("#d0743c"),
                                            new dimple.color("#7b6888"), new dimple.color("#266419"), new dimple.color("#DF7821"), new dimple.color("#4DA4DA"),
                                            new dimple.color("#A5C59E"), new dimple.color("#5C5596"), new dimple.color("#CA9A9A"), new dimple.color("#D8E4EA"),
                                            new dimple.color("#326277"), new dimple.color("#9174A5"), new dimple.color("#7B0404"), new dimple.color("#EAE2EF"),
                                            new dimple.color("#562323"), new dimple.color("#03671F"), new dimple.color("#7b6888"), new dimple.color("#E3F25E"),
                                            new dimple.color("#F498DA"), new dimple.color("#6b486b") ];

                var orange_colors = ["rgb(182, 102, 54)","rgb(186, 87, 28)",
                                "rgb(202, 85, 16)","rgb(236, 98, 17)","rgb(253, 101, 12)","rgb(253, 128, 54)","rgb(252, 143, 52)",
                                "rgb(252, 181, 73)","rgb(252, 217, 143)","rgb(240, 168, 13)","rgb(253, 175, 7)","rgb(247, 202, 104)",
                                "rgb(224, 136, 18)","rgb(247, 232, 154)","rgb(247, 187, 108)","rgb(240, 209, 161)"];
                var blue_colors = ["rgb(6, 67, 86)","rgb(15, 88, 184)","rgb(11, 105, 132)","rgb(71, 122, 190)","rgb(37, 134, 163)","rgb(50, 158, 190)",
                                   "rgb(58, 180, 216)","rgb(64, 198, 237)","rgb(102, 215, 249)","rgb(140, 223, 247)","rgb(176, 235, 252)" ];

                var purple_colors = ["rgb(48, 17, 87)","rgb(88, 35, 115)","rgb(121, 28, 136)","rgb(129, 58, 140)","rgb(160, 78, 173)","rgb(183, 39, 207)",
                                   "rgb(224, 63, 250)","rgb(232, 111, 252)","rgb(239, 153, 253)","rgb(242, 192, 250)" ];

                var green_colors = ["rgb(40, 60, 6)","rgb(58, 84, 13)","rgb(82, 118, 20)","rgb(91, 144, 1)","rgb(101, 144, 29)","rgb(124, 179, 30)",
                                   "rgb(155, 219, 42)","rgb(170, 219, 84)","rgb(189, 240, 100)","rgb(102, 215, 249)","rgb(201, 249, 119)","rgb(217, 250, 159)" ];

                var red_colors = ["rgb(77, 7, 7)","rgb(95, 9, 9)","rgb(111, 0, 0)","rgb(145, 12, 12)","rgb(174, 2, 2)","rgb(194, 12, 12)",
                                   "rgb(221, 23, 23)","rgb(249, 13, 13)","rgb(253, 35, 35)","rgb(252, 63, 63)","rgb(247, 104, 104)","rgb(247, 162, 162)" ];

                var black_colors = ["rgb(8, 7, 7)","rgb(39, 33, 33)","rgb(63, 54, 54)","rgb(81, 74, 74)","rgb(94, 88, 88)","rgb(113, 108, 108)",
                                   "rgb(142, 139, 139)","rgb(169, 166, 166)","rgb(194, 189, 189)","rgb(252, 63, 63)","rgb(216, 213, 213)","rgb(239, 234, 234)" ];

                var color_dict = {"Communication/Socializing": blue_colors,
                              "Fun/Leisure/Hobbies": orange_colors,
                              "Responsibilities": red_colors,
                              "Self-care/Everyday Needs": black_colors,
                              "Transportation": purple_colors,
                              "Sports/Fitness": green_colors
                };
                var prev_category = "";
                var counter = 0;
                $.each(response[0], function(i, e) {
                    chartInner.assignColor(e.Category, e.Color);
                });
                $.each(response[1], function(i, e) {
                    if (e.Category != prev_category){
                        counter = 0
                    }
                    chartOuter.assignColor(e.Activity, color_dict[e.Category][counter%16]);
                    prev_category = e.Category;
                    counter += 1;
                });

                chartOuter.draw();
                chartInner.draw();

                $(window).on('resize', function() {
                    chartOuter.draw(0, true);
                    chartInner.draw(0, true);
                });

                $('select[name="metric-select"]').on('change', function() {
					var metric = $('#metric-select').val();
					if ( metric == "Number of Instances") {
						outer_p.measure = "Instances";
						inner_p.measure = "Instances";
					}
					else{
						outer_p.measure = "Hours";
						inner_p.measure = "Hours";
					}
					chartOuter.draw();
					chartInner.draw();
    			});

			}
	    });
     };

 /**************************************************************************************/

    function updatePlacesBanner(place_selected) {
        var range = $('#dateRange').val();
        $.ajax({
            type: "post",
            data: {range: range, csrfmiddlewaretoken: getCookie('csrftoken'), place: place_selected, radius:$('#radius-select').data('slider').getValue()},
            cache: false,
            url: BASE_URL + 'analytics/places/update/places_chartbanner/',
            dataType: "json",
            error: function (xhr, status, error) {
                Done();
                console.log('went bad');
            },
            success: function (response) {
                $('#totalActivities').text(response.total_activities);
                $('#totalActivitiesNearPlaces').text(response.total_activities_done_near_places);
                $('#totalParticipationNearPlaces').text(response.percentage_of_activities_near_places.toFixed(1) + "%");
                $('#totalTimeNearPlaces').text(response.total_time_spent_near_places);
                $('#date-range-total-analytics').text(range);

                if (place_selected == "all"){
                    $('#totalActivitiesLabel').text("Total Activities performed:");
                    $('#totalActivitiesNearPlacesLabel').text("Total Activities done near Places:");
                    $('#totalParticipationNearPlacesLabel').text("Activity Percentage near Places:");
                    $('#totalTimeNearPlacesLabel').text("Total Time spent near Places:");
                }
                else{
                    if (place_selected != "Everywhere else") {
                        $('#totalActivitiesNearPlacesLabel').text("Activities near selected Place:");
                        $('#totalParticipationNearPlacesLabel').text("Activity Percentage of sel. Place:");
                        $('#totalTimeNearPlacesLabel').text("Time spent near selected Place:");
                    }
                    else{
                        $('#totalActivitiesNearPlacesLabel').text("Activities outside your Places:");
                        $('#totalParticipationNearPlacesLabel').text("Activity percentage outside Places:");
                        $('#totalTimeNearPlacesLabel').text("Time spent outside your Places:");
                    }
                }
            }
        });
    }

    /******************************************************************************************************/
    function PlacesCategoryDistributionBarChart() {
        var range = $('#dateRange').val();
        var metric = $('#metric-select').val();
        var radius = $('#radius-select').data('slider').getValue();
        $('.analytics-bottomChart h1').text('Individual Place Analysis');
		$.ajax({
			type: "post",
			data: { radius: radius, csrfmiddlewaretoken: getCookie('csrftoken'), range: range},
			cache: false,
			url: BASE_URL + 'analytics/places/update/places_all/',
			dataType: "json",
			error: function (xhr, status, error) {
				Done();
				console.log('went bad');
			},
			success: function (response) {
                try {
                    svg2.selectAll('*').remove();
                }
                catch(err) {}
                var placesBarChart = new dimple.chart(svg2, response);
                placesBarChart.setMargins("60px", "30px", "110px", "70px");
				placesBarChart.setBounds('10%', '10%', '85%', '73%');
                var x = placesBarChart.addCategoryAxis("x", "Place");
                x.title = "Category Analysis for Places in desc order"
                if (metric == "Number of Instances") {
                    x.addOrderRule("Instances", true);
                    var y = placesBarChart.addMeasureAxis("y", "Instances");
                }
                else {
                    x.addOrderRule("Hours", true);
                    var y = placesBarChart.addMeasureAxis("y", "Hours");
                }
                ;
                placesBarChart.addLegend("5%", 20, "90%", "5%", "right");
				placesBarChart.addSeries("Category", dimple.plot.bar);
                $.each(response, function(i, e) {
                    placesBarChart.assignColor(e.Category, e.Color);
                });
                placesBarChart.draw();

                $(window).on('resize', function() {
                    placesBarChart.draw(0, true);
                });

                 $('select[name="metric-select"]').on('change', function() {
					var metric = $('#metric-select').val();
					if ( metric == "Number of Instances") {
                        y.measure = "Instances";
                        y.tickFormat = '';
                        x._orderRules[0].ordering = "Instances";
					}
					else{
                        y.measure = "Hours";
                        y.tickFormat = ',.2f';
                        x._orderRules[0].ordering = "Hours";
					}
					placesBarChart.draw();
    			});
			}
	    });
    }
        var map;
        var markers=[];
        var circles = [];
		function initializeAnalyticsPlacesMap(map_data) {
			var mapCanvas = document.getElementById('map-canvas');
			var mapOptions = {
			  center: {lat:20, lng:20},
			  zoom: 16
			};
			map = new google.maps.Map(mapCanvas, mapOptions);
		}
        google.maps.event.addDomListener(window, 'load', initializeAnalyticsPlacesMap);

        function updateMarkers(marker_data, place_data, map) {

            for (var i = 0; i < markers.length; i++ ) {
                    markers[i].setMap(null);
            }
            for (i = 0; i < circles.length; i++ ) {
                    circles[i].setMap(null);
            }
            markers = [];
            circles = [];
            var infowindow = new google.maps.InfoWindow;
            for (i = 0; i < marker_data.length; i++) {
                var marker = new google.maps.Marker({});
                marker.setPosition({lat: marker_data[i].lat, lng: marker_data[i].lng});
                if (marker_data[i].pinColor != "black") {
                    marker.setIcon('http://google.com/mapfiles/ms/micons/' + marker_data[i].pinColor + '-dot.png');
                }
                else {
                    marker.setIcon('http://www.google.com/intl/en_ALL/mapfiles/marker_grey.png');
                }
                marker.setMap(map);
                markers.push(marker);


                google.maps.event.addListener(marker, 'click', (function (marker, i) {
                    return function () {
                        var content = "<p><b>Activity: </b>" + marker_data[i].activity + "</p>"+
                                      "<p><b>Start Date: </b>" + marker_data[i].start_date + "</p>" +
                                      "<p><b>Duration: </b>" + marker_data[i].duration + "</p>";
                        infowindow.setContent(content);
                        infowindow.open(map, marker);
                    }
                })(marker, i));
            }

            for (i = 0; i < place_data.length; i++) {
                var marker = new google.maps.Marker({});
                marker.setPosition({lat: place_data[i].lat, lng: place_data[i].lng});
                marker.setMap(map);
                marker.setIcon("http://maps.google.com/mapfiles/kml/pal3/icon31.png");
                markers.push(marker);


                google.maps.event.addListener(marker, 'click', (function (marker, i) {
                    return function () {
                        var content = "<p><b>Place: </b>" + place_data[i].Place + "</p>";
                        infowindow.setContent(content);
                        infowindow.open(map, marker);
                    }
                })(marker, i));

                var populationOptions = {
                    strokeColor: '#FFFFFF',
                    strokeOpacity: 0,
                    strokeWeight: 0,
                    fillColor: '#FF0000',
                    fillOpacity: 0.2,
                    map: map,
                    center: {lat:place_data[i].lat, lng:place_data[i].lng},
                    radius: $('#radius-select').data('slider').getValue() * 1000
                };
                // Add the circle for this city to the map.
                circles.push(new google.maps.Circle(populationOptions))

            }

            var bounds = new google.maps.LatLngBounds();
            for(i=0;i<markers.length;i++) {
                bounds.extend(markers[i].getPosition());
            }

            for(i=0;i<circles.length;i++) {
                bounds.union(circles[i].getBounds());
            }

            //center the map to the geometric center of all markers
            map.setCenter(bounds.getCenter());
            map.fitBounds(bounds);
            // set a maximum zoom
            if(map.getZoom()> 16){
              map.setZoom(16);
            }
        }

    function updatePlacesChartsAndBanner(){
         if ($("#allPlacesChecked").prop('checked')) {

            $('#place-select').prop('disabled', true).trigger("chosen:updated");
            ActivitiesInPlaceDonutChart('all');
            PlacesCategoryDistributionBarChart();
            updatePlacesBanner('all');
        }
        else {
            $('#place-select').prop('disabled', false).trigger("chosen:updated");
            ActivitiesInPlaceDonutChart($('#place-select').val());
            updatePlacesBanner($('#place-select').val());
        }
    }

    $('#radius-select').slider({
        min: 0.5,
        max: 20,
        step: 0.5,
        value: 6,
        formater: function(value) {
            return 'Distance up to: ' + value + ' km';
        }
    }).on('slideStop', function(evt){
        updatePlacesChartsAndBanner();
    });


    $('#dateRange').val('01/01/2015 - ' + moment().format("MM/DD/YYYY"));
	$('#dateRange').daterangepicker({
		format: 'MM/DD/YYYY',
		startDate: moment().startOf('year'),
		endDate: moment(),
		/*sshowDropdowns: true,*/
		ranges: {
		   'Today': [moment(), moment()],
		   'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
		   'Previous Week': [moment().subtract(1, 'week').startOf('week').add(1,'day'), moment().subtract(1,'week').endOf('week').add(1,'day')],
		   'Previous Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')],
           'Month to Date': [moment().startOf('month'), moment()],
           'Year to Date': [moment().startOf('year'), moment()]
		},
		locale: {
			monthNames: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
			fromLabel: 'From',
			toLabel: 'To',
			customRangeLabel: 'Custom Range'
		}
	});


    $(window).on('load', function(){
        $('#dateRange').trigger('change');
    });