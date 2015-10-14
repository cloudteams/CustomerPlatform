$(function() {
    $('select').chosen();

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
    $('.work-city input').autocomplete({
        source: function( request, response ) {
            $.ajax({
                url: "https://api.teleport.org/api/cities/?search=" + request.term,
                dataType: "json",
                minLength: 3,
                beforeSend: function(){
                    $('.work-city-select').empty();
                },
                success: function( data ) {
                    var options = data['_embedded']['city:search-results'];
                    for (var i=0; i < options.length; i++) {
                        console.log(options[i].matching_full_name)
                        $('.work-city-select').append('<li class="active-result">' + options[i].matching_full_name + '</li>');
                    }

                    $('.work-city-select').css('display', 'block');
                    console.log($('.work-city input').offset().left)
                    $('.work-city-select').css('left', $('.page-container').offset().left + $('.work-city input').position().left);
                    $('.work-city-select').css('top', $('.page-container').offset().top + $('.work-city input').position().top + 30);
                }
            });
        }
    }).autocomplete("widget").addClass("work-city-select");;
});