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

        //influences
        'FAMILY': 'fa-child',
        'FRIENDS': 'fa-group',
        'BLOGS': 'fa-file-text',
        'TV': 'fa-television',
        'ADS': 'fa-volume-up',
        'COWORKERS': 'fa-building-o',
        'OTHER': 'fa-ellipsis-h'
    },

    init: function(selector, options) {
        options = options || {};
        options.style = options.style || 'icons';

        // hide the actual select
        $(selector).css('display', 'none');

        //foreach select in the selector
        for (var i=0; i<$(selector).length; i++) {
            //add a container for the options
            var select = $($(selector)[i]);
            select.parent().append('<div class="opt-container"></div>');
            var opt_container = $(select).parent().find('.opt-container');

            //add all options in the container
            cnt = 0;
            for (var j=0; j < select.find('option').length; j++) {
                var opt = $(select.find('option')[j]);
                if (!opt.val()) {
                    continue;
                }
                cnt++;

                var opt_div = '<div class="option';
                if (opt.is(':selected')) {
                    opt_div += ' option-active';
                }
                opt_div += '" data-value="' + opt.val() + '">';
                if (options.style == 'icons') {
                    if (this.icons[opt.val()]) {
                        opt_div += '<span class="fa ' + this.icons[opt.val()] + ' fa-4x"></span>'
                    }
                } else if (options.style == 'numbers') {
                    opt_div += '<i class="number-icon">' + (cnt) + '</i>'
                }

                opt_div += opt.text() + '</div>';

                $(opt_container).append(opt_div);

                if (typeof(options.break_after) != "undefined") {
                    if (options.break_after.indexOf(j) >= 0) {
                        $(opt_container).append('<div class="option-seperator"></div>');
                    }
                }
            }
        }
    }
};

$(function() {
    //on select
    $('body').on('click', '.opt-container > .option:not(.option-active)', function() {
        //check if other options have to be cleared first
        if (!$(this).parent().parent().find('select').attr('multiple')) {
            $(this).parent().parent().find('select > option').attr('selected', false);
            $(this).siblings().removeClass('option-active')
        }

        $(this).addClass('option-active');
        $(this).parent().parent().find('select > option[value="' + $(this).data('value') + '"]').attr('selected', true);
        $(this).parent().parent().find('select').change();
    });

    //on un-select
    $('body').on('click', '.opt-container > .option.option-active', function() {
        $(this).removeClass('option-active');
        $(this).parent().parent().find('select > option[value="' + $(this).data('value') + '"]').attr('selected', false);
        $(this).parent().parent().find('select').change();
    });
});