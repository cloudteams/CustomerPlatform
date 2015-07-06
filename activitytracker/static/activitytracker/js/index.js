/**
 * Created by Aggelos.
 */

        $('.clockpicker').clockpicker();

        $('#friends').tokenize({
                placeholder: "With whom were you with?"
            });

        $('#tools').tokenize({
                placeholder: "What did you use?"
            });

        $('#showActivityModal').on("hidden", function (e) {
            $(e.target).removeData("modal").find(".modal-body").empty();
        });
        $('#editActivityModal').on("hidden", function (e) {
            $(e.target).removeData("modal").find(".modal-body").empty();
        });
        $('#showGroupActivityModal').on("hidden", function (e) {
            $(e.target).removeData("modal").find(".modal-body").empty();
        });
        $('#addActivityModal').on("hidden", function (e) {
            map.setCenter({ lat: 37.9908372, lng: 23.7383394});
            map.setZoom(9);
            marker.setMap(null);
	    marker.setPosition(null);
        });

        $(document).ready(function () {
            // executes when DOM is loaded and ready
            $("span.fc-button-prev").html("<span class='fc-button-inner'><span class='fc-button-content'>&nbsp;◄&nbsp;</span></span>");
            $("span.fc-button-next").html("<span class='fc-button-inner'><span class='fc-button-content'>&nbsp;►&nbsp;</span>");
            $("span.fc-button-today").html("<span class='fc-button-inner'><span class='fc-button-content'>today</span></span>");
            $("span.fc-button-month").html("<span class='fc-button-inner'><span class='fc-button-content'>month</span></span>");
            $("span.fc-button-agendaWeek").html("<span class='fc-button-inner'><span class='fc-button-content'>week</span></span>");
            $("span.fc-button-agendaDay").html("<span class='fc-button-inner'><span class='fc-button-content'>day</span></span>");
            $('.fc-header-right').append(jQuery.parseHTML("<a href='#' data-toggle='modal' data-target='#addActivityModal' onclick='clearFields()'> " +
            "<i class='icon-plus'></i>&nbsp&nbspadd another</a> "));
            if (show_carousel_guide == "True") {
                $('#carouselModal').modal('show');
            }
        });


        /* add activity */
        $("#addActivityModalSubmit").click(function(event) {
            event.preventDefault();
            Loading();
            var data = submitFields('addForm', getCookie('csrftoken'));
            try {
                data.lat = marker.getPosition().lat();
                data.lng = marker.getPosition().lng()
            }
            catch(err) {
                data.lat = null;
                data.lng = null;
            }
            $.ajax({
                type: "post",
                data: data,
                cache: false,
                url: BASE_URL + 'activity/add/',
                dataType: "text",
                error: function (xhr, status, error) {
                    Done();
                    alert(xhr.responseText);
                },
                success: function (response) {
                    var data = jQuery.parseJSON(response);
                    $('#main_calendar').fullCalendar('refetchEvents'); // re-render events
                    var viewInstance = $('#main_calendar').fullCalendar('getView');
                    RenderViewActivities(viewInstance); // redraws activities based on view
                    $('#addActivityModal .modal-body').scrollTop(0);
                    $('#addActivityModal').modal('hide');
                    Done();
                    document.getElementById("addForm").reset();
                    $('#name_of_activity').val('').trigger('liszt:updated');
                    $('#friends').data('tokenize').clear();
                    $('#tools').data('tokenize').clear();
                    $('#goalstatus').addClass('hidden');
                    marker.setPosition(null);

                }
            });
        });

        /* show activity fields */
        $('#showActivityModal').on("shown", function (e){
            var id_clicked = $('.modal-body-replacement').attr('id');
            var url_edit = BASE_URL + "activity/edit-activity/" + id_clicked;
            var url_json_activity = BASE_URL + "activity/" + id_clicked;
            $("#editactivity").attr("href", url_edit);
            $("#showActivityModal h2 a").attr("href", url_json_activity);
        });

        /* Delete Activity */
        $('a[href="/activitytracker/activity/delete-activity/"]').on("click", function(event){
            event.preventDefault();
            var id_clicked = $('.modal-body-replacement').attr('id');
            Loading();
            $.ajax({
                type: "post",
                data: {act_id: id_clicked, csrfmiddlewaretoken: getCookie('csrftoken')},
                cache: false,
                url: BASE_URL + "activity/delete-activity/",
                dataType: "text",
                error: function (xhr, status, error) {
                    DoneWithBackdrop();
                    alert('Something went wrong. Page will be refreshed');
                    window.location.reload();
                },
                success: function (response) {
                    var currentscrollpos = $(window).scrollTop();
                    $('#showActivityModal').modal('hide');
                    var viewInstance = $('#main_calendar').fullCalendar('getView');
                    RenderViewActivities(viewInstance); // redraws activities based on view
                    $('#main_calendar').fullCalendar( 'refetchEvents' ); // re-render events on Calendar
                    $("html, body").animate({ scrollTop: currentscrollpos }, 1300);
                    Done();
                }
            });

        });

        /* Update Activity */
        $("#editActivityModalSubmit").click( function(event){
            event.preventDefault();
            var id_clicked = $('.modal-body-replacement').attr('id');
            var data = submitFields('editForm', getCookie('csrftoken'));
            data.lat = markerEdit.getPosition().lat();
            data.lng = markerEdit.getPosition().lng();
            data.the_id = id_clicked;
            Loading();
            $.ajax({
                type: "post",
                data: data,
                cache: false,
                url: BASE_URL + "activity/update-activity/",
                dataType: "text",
                error: function (xhr, status, error) {
                    Done();
                    alert(xhr.responseText);
                },
                success: function (response) {
                    Done();
                    $('#editActivityModal').modal('hide');
                    var viewInstance = $('#main_calendar').fullCalendar('getView');
                    RenderViewActivities(viewInstance); // redraws activities based on view
                    $('#main_calendar').fullCalendar( 'refetchEvents' );
                }
            });

        });

        /* Group - Ungroup Activities */
        function GroupUngroupSort(){
            LoadingWithBackdrop();
            var ids = ShownIds();
            DrawGroupUngroupSort(ids);
            DoneWithBackdrop();
        }



        function ListTheActivities(){
            window.open(BASE_URL + "activity/listallactivities/", 'newwindow', 'width=300, height=300');
            return false;
        }



        $('#goalinput').on('keyup change',function() {
             if ( document.forms['addForm']["goal"].value.length == 0){
                 $('#goalstatus').addClass('hidden');
                 $('#InProgress').prop('checked',true);
             }
             else{
                 $('#goalstatus').removeClass('hidden')
             }
        });

    var map; // reference to Gmaps, can't be done without global/custom scope variable
    var marker; // reference to marker. Can't get reference to marker(s) from a map object => need for global var
    function initialize() {
        marker = new google.maps.Marker({
            position: {lat:0, lng:0},
            draggable: true
        });

        var mapOptions = {
            center: {lat: 37.9908372, lng: 23.7383394},
            zoom: 9
        };
        map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
        google.maps.event.addListener(marker, 'dragend', function (event) {

            marker.setMap(null);
            marker.position = event.latLng;
            map.setCenter(marker.position);
            marker.setMap(map);

            var geoLocations = (marker.getPosition().toString()).replace('(', '').replace(' ', '').replace(')', '');
            $.ajax({
                type: "get",
                cache: false,
                url: "http://maps.googleapis.com/maps/api/geocode/json?latlng=" + geoLocations,
                dataType: "json",
                error: function (xhr, status, error) {
                    alert("Couldn't fetch this Address. Try again!")
                },
                success: function (response) {
                    console.log(response);
                    $('#places-input').val(response.results[0].formatted_address)
                }
            });
        });

        var input = (document.getElementById('places-input'));
      //  map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);
        var searchBox = new google.maps.places.SearchBox((input));
        var defaultBounds = new google.maps.LatLngBounds(
                new google.maps.LatLng(-33.8902, 151.1759),
                new google.maps.LatLng(-33.8474, 151.2631));
        map.fitBounds(defaultBounds);

        google.maps.event.addListener(searchBox, 'places_changed', function () {
            var place = searchBox.getPlaces()[0]; // We dont want more than 1 markers
            if (place.length == 0) {
                return;
            }

            marker.setMap(null); // Nullify the previous marker
            // For only the 1st place, get the icon, place name, and location.
            var bounds = new google.maps.LatLngBounds();
            var image = {
                url: place.icon,
                size: new google.maps.Size(71, 71),
                origin: new google.maps.Point(0, 0),
                anchor: new google.maps.Point(17, 34),
                scaledSize: new google.maps.Size(25, 25)
            };

            // Move the marker to the new Location
            marker.position = place.geometry.location;
            marker.setMap(map);
            marker.setAnimation(google.maps.Animation.DROP);

            bounds.extend(place.geometry.location);

            map.fitBounds(bounds);
            map.setZoom(16);
        });

        google.maps.event.addListener(map, 'bounds_changed', function () {
            var bounds = map.getBounds();
            searchBox.setBounds(bounds);
        });
    }
    google.maps.event.addDomListener(window, 'load', initialize);

    $('#addActivityModal').on('shown', function () {
        google.maps.event.trigger(map, "resize");
        map.setCenter({ lat: 37.9908372, lng: 23.7383394});
        map.setZoom(9);

    });






