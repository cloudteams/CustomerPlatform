$(function() {
    //chosen
    $('select:not(#id_platforms, #id_devices, #id_influences, #id_tech_level)').chosen();

    //nice options
    NiceOpts.init('#id_platforms, #id_devices, #id_influences');
    NiceOpts.init('#id_tech_level', {
        style: 'numbers'
    });

    //paginate
    $('.wizard-page-container').bjqs({
        animtype    : 'slide',
        height      : 600,
        width       : $('.breadcrumb').width(),
        responsive  : true,
        animspeed   : 999999
    });

    //input class
    $('.create-profile-form input').addClass('input-lg form-control');

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
                success: function(data) {
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

                    var inp = $(this)[0].element;
                    $('.city-select').css('display', 'block');
                    $('.city-select').css('left', $('.wizard-page-container').offset().left + $(inp).position().left);
                    $('.city-select').css('top', $('.wizard-page-container').offset().top + $(inp).position().top + 30);
                }
            });
        }
    }).autocomplete("widget").addClass("city-select");

    //opinions
    $.ajax({
        url: '/profile/get-brand-opinion',
        success: function (data) {
            $('#tech-opinion').html(data);
            if (data == '') {
                $('.brand-opinions-field').hide();
            }
        }
    });

    $('body').on('click', '.send-opinion', function() {
        var brand = $(this).closest('form').find('input[name="brand"]').val();
        var opinion = $(this).data('value');
        var csrfmiddlewaretoken = $(this).closest('form').find('input[name="csrfmiddlewaretoken"]').val();

        $('#tech-opinion').css('opacity', '0');

        $.ajax({
            url: '/profile/opinion-about',
            method: 'POST',
            data: {
                csrfmiddlewaretoken: csrfmiddlewaretoken,
                brand: brand,
                opinion: opinion
            },
            success: function() {
                //get another opinion
                $.ajax({
                    url: '/profile/get-brand-opinion',
                    success: function (data) {
                        $('#tech-opinion').html(data);
                        $('#tech-opinion').css('opacity', '1');
                    }
                });
            }
        })
    });
});