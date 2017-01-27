/**
 * Created by dimitris on 27/1/2017.
 */
$(function() {
    $('#contact-team-popup .confirm-button').on('click', function(e) {

        var $form = $('#contact-team-popup'),
            projectId = $form.data('projectid'),
            providedInfo = $form.find('#id_contact_provided_info').val(),
            message = $form.find('#id_contact_message').val(),
            csrftoken = $form.find('input[name="csrfmiddlewaretoken"]').val();

        if (providedInfo == '') {
            e.preventDefault();
            e.stopPropagation();

            return
        }

        // replace contact button
        $('[data-target=".contact-team-form-popup"]').replaceWith('<div class="btn-grey"><i class="fa fa-check green-text"></i> Contacted project members</div>');

        // send request
        $.ajax({
            url: '/projects/' + projectId + '/contact-team/',
            method: 'POST',
            data: {
                provided_info: providedInfo,
                message: message,
                csrfmiddlewaretoken: csrftoken
            }
        })
    })
});