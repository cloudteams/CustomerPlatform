$(function() {
    NiceOpts.init('#influences-view, #devices-view, #platforms-view', {
        size: 2,
        disabled: true
    });

    if ($('aside .bottom').position().top < 380) {
        $('aside .bottom').attr('style', 'top: 380px;');
    }

    // Invitations
    $('form.invitation-form').on('submit', function(e) {
        var $form = $(this),
            $btn = $form.find('button[type="submit"]');

        // send invitation request
        var name = $form.find('input[name="invited_name"]').val(),
            email = $form.find('input[name="invited_email"]').val();

        // prevent multiple submissions
        if ($btn.hasAttr('disabled')) {
            e.preventDefault()
            return false
        }

        // make button disabled
        $btn.attr('disabled', 'disabled')
        $btn.find('i').removeClass('fa-envelope').addClass('fa-spin fa-spinner')
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
                $btn.find('i').removeClass('fa-spin fa-spinner').addClass('fa-envelope')
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
                $btn.find('i').removeClass('fa-spin fa-spinner').addClass('fa-envelope')
                $btn.find('span').text('Send invitation')
            }
        })

        // prevent default submission
        e.preventDefault();
        return false;
    })
});