$(function() {
    /* On post idea button click */
    $('.show-idea-form').on('click', function(e) {
        $(this).toggle();
        $('.form-post-idea').toggle();
    });

    /* On cancel, show the button again */
    $('.hide-idea-form').on('click', function(e) {
        var form = $(this).closest('.form-post-idea');
        form.toggle();
        form.parent().find('.show-idea-form').toggle();
    });
});