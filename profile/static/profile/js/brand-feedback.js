$(function() {
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

    /* Send an opinion about a brand */
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