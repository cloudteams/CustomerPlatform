/**
 * Created by dimitris on 26/1/2017.
 */
$(function() {

    /* On buy click */
    $('.reward-purchase-btn').on('click', function() {
        // get teaser
        var $teaser = $(this).closest('.reward-teaser'),
            rewardId = $teaser.data('id'),
            rewardName = $teaser.find('.reward-header .reward-name').text(),
            rewardDescription = $teaser.find('.reward-content > p').attr('title'),
            projectName = $teaser.find('.project-name').text(),
            cost = $teaser.find('.reward-cost').text();

        // update purchase form
        var $popup = $('#buy-a-reward'),
            $popupSection1 = $popup.find('section.confirm-1');

        $popupSection1.find('.reward-id').text(rewardId);
        $popupSection1.find('.reward-name').text(rewardName);
        $popupSection1.find('.reward-description').text(rewardDescription);
        $popupSection1.find('.project-name').text(projectName);
        $popupSection1.find('.reward-cost').text(cost);
    });

    /* On buy confirm */
    $('.confirm-purchase').on('click', function() {
        var $popup = $('#buy-a-reward'),
            $popupSection1 = $popup.find('section.confirm-1'),
            $popupSection2 = $popup.find('section.confirm-2'),
            rewardId = $popupSection1.find('.reward-id').text(),
            cost = Number($popupSection1.find('.reward-cost').text()),
            currentBalance =  Number($($('.user-current-balance').get(0)).text()),
            csrfToken = $popup.find('input[name="csrfmiddlewaretoken"]').val();

        // loading animation
        $popupSection2.
            find('.col-md-12.text-center').
            html('<i class="loader-general loader-general-gray"></i> <span class="loader-message"> Purchasing reward...</span>');

        // toggle section
        $popupSection1.hide();
        $popupSection2.show();

        // perform the request
        $.ajax({
            url: '/projects/rewards/purchase/' + rewardId + '/',
            type: 'POST',
            data: {
                csrfmiddlewaretoken: csrfToken
            },
            success: function(purchaseRow) {

                // update balance, remove teaser
                $('.user-current-balance').text(currentBalance - cost);
                $('.reward-teaser[data-id="' + rewardId + '"]').remove();

                // remove placeholder purchase if exists
                $('.purchase-placeholder').remove();

                // add transaction to table
                var $table = $('.bought-rewards-content-row'),
                    $purchaseRow = $(purchaseRow);

                $table.append($purchaseRow);

                // update modal
                var $container = $popupSection2.find('.col-md-12.text-center');
                $container
                    .empty()
                    .append('<p>Succesfully purchased!</p>')
                    .append('<a href="' + $purchaseRow.find('.reward-download-link').attr('href') +  '" target="_blank" class="btn"><i class="icon icon-download"></i> Download</a>')
                    .append('<p>You can find this reward on your <a href="/projects/rewards/?tab=purchased" class="purple-link">Reward page</a></p>');
            },
            error: function(error) {
                var message = error.responseText,
                    messageAlt = '';

                if (message.indexOf('enough CloudCoins') >= 0) {
                    message = message.replace('CloudCoins!', '<i class="icon icon-cloudcoins"></i>');
                    messageAlt = '<p>Participate in <a href="/projects/dashboard/campaigns/?tab=running" class="purple-link">open campaigns</a> to collect CC and buy your favourite rewards!</p>'
                }

                $popupSection2
                    .find('.col-md-12.text-center')
                    .html('<div style="color: #ff5071; font-size: 16px;"><i class="fa fa-times"></i> ' + message + '</div>' + messageAlt);
            }
        })
    });

    /* On popup close */
    $('.purchase-close').on('click', function() {
        var $popup = $('#buy-a-reward'),
            $popupSection1 = $popup.find('section.confirm-1'),
            $popupSection2 = $popup.find('section.confirm-2');

        // toggle section
        $popupSection2.hide();
        $popupSection1.show();

        setTimeout(function() {
            $('body').css('paddingRight', 0);
        }, 400);
    });
});