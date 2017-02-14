/**
 * Created by Aggelos.
 */




    function getActivities(place_selected) {
        var range = '01/01/2016 - ' + moment().format("MM/DD/YYYY");

        $.ajax({
            type: "post",
            data: { csrfmiddlewaretoken: getCookie('csrftoken'), range: range },
            cache: false,
            url: BASE_URL + 'analytics/places/update/categories_activities/',
            dataType: "json",
            error: function (xhr, status, error) {
                Done();
                console.log('went bad');
            },
            success: function (response) {
                updateMarkers(response[2], response[3], map);
            }
        });
    }

 /**************************************************************************************/

        var map;
        var markers=[];
        var circles = [];
		function initializeAnalyticsPlacesMap(map_data) {
			var mapCanvas = document.getElementById('map-canvas');
			var mapOptions = {
			  center: {lat:44.8408466, lng:15.7434564},
			  zoom: 5
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
                    marker.setIcon('http://maps.google.com/mapfiles/ms/micons/' + marker_data[i].pinColor + '-dot.png');
                }
                else {
                    marker.setIcon('http://www.google.com/intl/en_ALL/mapfiles/marker_grey.png');
                }
                marker.setMap(map);
                markers.push(marker);


                google.maps.event.addListener(marker, 'click', (function (marker, i) {
                    return function () {
                        var content = "<p><b>Activity: <span style='color: #7d3c8c;'>" + marker_data[i].activity + "</span></p>"+
                                      "<p><b>Start Date: <span style='color: #7d3c8c;'>" + marker_data[i].start_date + "</span></p>" +
                                      "<p><b>Duration: <span style='color: #7d3c8c;'>" + marker_data[i].duration + "</span></p>";
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

    $(window).on('load', function(){
        getActivities();
    });