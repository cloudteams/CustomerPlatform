console.log('in!')
$(function() {
    $('.minimize-toggle').click(function() {
        $('.dashboard-side-menu').toggleClass('minimized');
        if ($('.dashboard-side-menu').hasClass('minimized')) {
            $(this).find('.arrow').html('❯')
        } else {
            $(this).find('.arrow').html('❮')
        }
    })
})