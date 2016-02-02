$(function() {
    //chosen
    $('select:not(#id_platforms, #id_devices, #id_influences, #id_tech_level)').chosen();

    //nice options
    NiceOpts.init('#id_platforms, #id_devices');
    NiceOpts.init('#id_influences', {break_after: [2]});
    NiceOpts.init('#id_tech_level', {
        style: 'numbers'
    });

    //input class
    //$('.create-profile-form input').addClass('input-lg form-control');

    //trigger file selection
    $('#trigger-avatar-upload').click(function() {
        $('#id_profile_picture').click();
    });

    //autocomplete cities
    $('.work-city input, #id_location').attr('autocomplete', 'false')
    $('.work-city input, #id_location').autocomplete({
        source: function( request, response ) {
            var that = this;
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

                    var inp = $(that)[0].element;
                    $('.city-select').css('display', 'block');
                    $('.city-select').css('left', $(inp).offset().left);
                    $('.city-select').css('top', $(inp).offset().top + $(inp).outerHeight() - 1);
                }
            });
        }
    }).autocomplete("widget").css('width', '200px').addClass("city-select");

    /* On scroll update menu */
    $('.create-profile-form').scroll(function() {
        var st = $(this).scrollTop();
        var lis = $(this).find('ul.profile-wizard-paginator > li');

        $('ul.main-menu li').removeClass('active');
        for (var i=0; i<lis.length; i++) {
            if ($(lis[i]).offset().top >= 0) { // find which is currently visible
                $('ul.main-menu li a[href="#' + $(lis[i]).find('div').attr('id') + '"]').parent().addClass('active');
                break;
            }
        }
    });

    /* Save form automatically */
    ProfileFormManager = {
        avatar_updated: false,

        post_profile: function() {
            $('.profile-save-msg').html('Saving... <i class="fa fa-spinner fa-pulse"></i>')
            $.ajax({
                url: '.',
                method: 'POST',
                data: new FormData($('.create-profile-form')[0]),
                contentType: false,
                processData: false,
                success: function(data) {
                    $('.profile-save-msg').html('Saved <i class="fa fa-check"></i>');
                    ProfileFormManager.avatar_updated = false;
                },
                error: function() {
                    $('.profile-save-msg').html('<span class="alert-danger save-error-retry" role="alert"><span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span><span class="sr-only">Error:</span>Error while saving, try again</span>');
                }
            });
        }
    };

    $('.create-profile-form input').on('focusout', ProfileFormManager.post_profile);
    $('.create-profile-form select').on('change', ProfileFormManager.post_profile);
    $('body').on('click', '.save-error-retry', ProfileFormManager.post_profile);

    //preview avatar image
    $("#id_profile_picture").change(function(){
        if (this.files && this.files[0]) {
            var reader = new FileReader();

            reader.onload = function (e) {
                $('#avatar-container .avatar-img').css('background-image', 'url(' + e.target.result + ')');
            }

            reader.readAsDataURL(this.files[0]);
            ProfileFormManager.avatar_updated = true;
            ProfileFormManager.post_profile();
        }
    });
});