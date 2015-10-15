var NiceOpts = {
    icons: {
        //devices
        'PC': 'fa-desktop',
        'TB': 'fa-tablet',
        'LT': 'fa-laptop',
        'MF': 'fa-mobile',
        'WE': 'fa-clock-o',

        //platforms
        'MSWIN': 'fa-windows',
        'OSX': 'fa-apple',
        'LINUX': 'fa-linux',
        'IOS': 'fa-apple',
        'ANDR': 'fa-android',
    },

    init: function(selector) {
        // hide the actual select
        $(selector).css('display', 'none');

        //foreach select in the selector
        for (var i=0; i<$(selector).length; i++) {
            //add a container for the options
            var select = $($(selector)[i]);
            select.parent().append('<div class="opt-container"></div>');
            var opt_container = $(select).parent().find('.opt-container');

            //add all options in the container
            for (var j=0; j < select.find('option').length; j++) {
                var opt = $(select.find('option')[j]);
                var opt_div = '<div class="option';
                if (opt.is(':selected')) {
                    opt_div += ' option-active';
                }
                opt_div += '" data-value="' + opt.val() + '">';
                if (this.icons[opt.val()]) {
                    opt_div += '<span class="fa ' + this.icons[opt.val()] + ' fa-4x"></span>'
                }
                opt_div += opt.text() + '</div>';

                $(opt_container).append(opt_div);
            }
        }
    }
};

$(function() {
    //on select
    $('body').on('click', '.opt-container > .option:not(.option-active)', function() {
        $(this).addClass('option-active');
        console.log('select > option[value="' + $(this).data('value') + '"]')
        $(this).parent().parent().find('select > option[value="' + $(this).data('value') + '"]').attr('selected', true);
    });

    //on un-select
    $('body').on('click', '.opt-container > .option.option-active', function() {
        $(this).removeClass('option-active');
        $(this).parent().parent().find('select > option[value="' + $(this).data('value') + '"]').attr('selected', false);
    });
});