$(function() {
    //chosen
    $('select:not(#id_platforms, #id_devices)').chosen();

    //nice options
    NiceOpts.init('#id_platforms, #id_devices');

    //paginate
    $('.page-container').bjqs({
        animtype    : 'slide',
        height      : 500,
        width       : $('.create-profile-form').width(),
        responsive  : true,
        animspeed   : 999999
    });

    //preview avatar image
    $("#id_profile_picture").change(function(){
        if (this.files && this.files[0]) {
            var reader = new FileReader();

            reader.onload = function (e) {
                $('#avatar-container').html('<img src="' + e.target.result + '"/>');
            }

            reader.readAsDataURL(this.files[0]);
        }
    });

    //trigger file selection
    $('#trigger-avatar-upload').click(function() {
        $('#id_profile_picture').click();
    });

    //autocomplete cities
    $('.work-city input, #id_location').autocomplete({
        source: function( request, response ) {
            $.ajax({
                url: "https://api.teleport.org/api/cities/?search=" + request.term,
                dataType: "json",
                minLength: 3,
                beforeSend: function(){
                    $('.city-select').empty();
                },
                success: function( data ) {
                    var options = data['_embedded']['city:search-results'];
                    /*for (var i=0; i < options.length; i++) {
                        console.log(options[i].matching_full_name)
                        $('.work-city-select').append('<li class="active-result">' + options[i].matching_full_name + '</li>');
                    }*/
                    response($.map( options, function(item) {
                        return {
                            label: item.matching_full_name,
                            value: item.matching_full_name,
                        };
                    }));

                    $('.city-select').css('display', 'block');
                    $('.city-select').css('left', $('.page-container').offset().left + $('.work-city input').position().left);
                    $('.city-select').css('top', $('.page-container').offset().top + $('.work-city input').position().top + 30);
                }
            });
        }
    }).autocomplete("widget").addClass("city-select");;
});