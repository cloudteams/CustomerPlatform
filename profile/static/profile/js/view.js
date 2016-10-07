$(function() {
    NiceOpts.init('#influences-view, #devices-view, #platforms-view', {
        size: 2,
        disabled: true
    });

    if ($('aside .bottom').position().top < 380) {
        $('aside .bottom').attr('style', 'top: 380px;');
    }
});