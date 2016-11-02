/**
 * Created by dimitris on 2/11/2016.
 */
$(function() {
    /* Invitations */
    $('form.delete-account-form').on('submit', function(e) {
        var $form = $(this),
            $btn = $form.find('button[type="submit"]');

        // get confirmation text
        var confirm = $form.find('input[name="delete_confirm"]').val();

        // prevent multiple submissions
        if (confirm !== "DELETE") {
            $form.find('ul.errorlist').remove();
            $form.prepend('<ul class="errorlist"><li><i class="fa fa-exclamation-triangle"></i> Confirmation is required to delete your account.</li></ul>');

            e.preventDefault();
            return false
        }

        // prevent multiple submissions
        if ($btn.is('[disabled="disabled"]')) {
            e.preventDefault();
            return false
        }

        // prevent multiple submissions
        if ($btn.is('[disabled="disabled"]')) {
            e.preventDefault();
            return false
        }

        // make button disabled
        $btn.attr('disabled', 'disabled');
        $btn.find('span').text('Deleting account...');

        // form should now submit
    });
});