$(function() {
    /* Dashboard folding back */
    $('.minimize-toggle').click(function() {
        $('.dashboard-side-menu').toggleClass('minimized');
        $('section.page').toggleClass('minimized');
        if ($('.dashboard-side-menu').hasClass('minimized')) {
            $(this).find('.icon').removeClass('icon-arrow-left').addClass('icon-arrow-right')
        } else {
            $(this).find('.icon').addClass('icon-arrow-left').removeClass('icon-arrow-right')
        }
    })

    /* Search field on image click submit */
    $('body').on('click', 'header form.project-search svg', function() {
        console.log('in!')
        $(this).closest('form.project-search').submit();
    })

    /* Automatically close toggle */
    $('body').click(function(e) {
        $.each($('.open-tooltip-button.active'), function(idx, btn) {
            var $btn = $(btn);

            if ((!$btn.is(e.target))
                && ($btn.has(e.target).length === 0)) {
                $btn.click();
            }
        })

    });

    /* Modals */
    $('[data-toggle="modal"]').click(function() {
        $('#' + $(this).data('id')).modal('show')
    });

    /* Invitations */
    $('form.invitation-form').on('submit', function(e) {
        var $form = $(this),
            $btn = $form.find('button[type="submit"]');

        // send invitation request
        var name = $form.find('input[name="invited_name"]').val(),
            email = $form.find('input[name="invited_email"]').val();

        // prevent multiple submissions
        if ($btn.is('[disabled="disabled"]')) {
            e.preventDefault()
            return false
        }

        // make button disabled
        $btn.attr('disabled', 'disabled')
        $btn.find('i').removeClass('fa-envelope').addClass('loader-general loader-general-gray')
        $btn.find('span').text('Sending invitation...')

        $.ajax({
            type: 'POST',
            url: $form.attr('action'),
            data: {
                invited_name: name,
                invited_email: email,
                csrfmiddlewaretoken: $form.find('input[name="csrfmiddlewaretoken"]').val(),
            },
            success: function(data) {
                // clear form
                $form.find('.errorlist').remove()
                $form.find('input[name="invited_name"]').val('')
                $form.find('input[name="invited_email"]').val('')

                // hide invitation form
                $form.closest('.modal').modal('hide')

                // restore button
                $btn.removeAttr('disabled')
                $btn.find('i').removeClass('loader-general loader-general-gray').addClass('fa-envelope')
                $btn.find('span').text('Send invitation')

                // show success
                var $invitationSuccess = $('#invitation-success')
                $invitationSuccess.find('.to-email').text(email)
                $invitationSuccess.modal('show');
            },
            error: function(jqXHR) {
                var error = 'Something went wrong, please try again in a minute. Sorry for the inconvenience!'
                if (jqXHR.status == 400) { // validation error
                    error = jqXHR.responseText
                }

                var $errorMsg = '<ul class="errorlist"><li><i class="fa fa-exclamation-triangle"></i> ' + error + '</li></ul>'

                // add error
                var $errorList = $form.find('.errorlist')
                if ($errorList.length == 0) {
                    $form.prepend($errorMsg)
                } else {
                    $errorList.replaceWith($errorMsg)
                }

                // restore button
                $btn.removeAttr('disabled')
                $btn.find('i').removeClass('loader-general loader-general-gray').addClass('fa-envelope')
                $btn.find('span').text('Send invitation')
            }
        });

        // prevent default submission
        e.preventDefault();
        return false;
    });
})