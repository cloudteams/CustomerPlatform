$(function() {
    /* Dashboard folding back */
    $('.minimize-toggle').click(function() {
        $('.dashboard-side-menu').toggleClass('minimized');
        if ($('.dashboard-side-menu').hasClass('minimized')) {
            $(this).find('.arrow').html('❯')
        } else {
            $(this).find('.arrow').html('❮')
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

    })

    /* Modals */
    $('[data-toggle="modal"]').click(function() {
        $('#' + $(this).data('id')).modal('show')
    })
})