/**
 * Created by dimitris on 16/9/2016.
 */
$(function() {
    /* Show leaderboard */
    $('.btn[data-id="leaderboard-popup"]').on('click', function() {
        var $popupBody = $('#leaderboard-popup .modal-body');
        var $loading = $('<p style="text-align: center;"><i class="fa fa-spin fa-spinner"></i></p>');

        $popupBody.append($loading);

        // dynamically load the leaderboard
        $.ajax({
            url: '/gamification/leaderboard/',
            type: 'GET',
            success: function(data) {
                $popupBody.html(data);
            }
        })
    });

    /* Show badge collection */
    $('.btn[data-id="badge-collection-popup"]').on('click', function() {
        var $popupBody = $('#badge-collection-popup .modal-body');
        var $loading = $('<p style="text-align: center;"><i class="fa fa-spin fa-spinner"></i></p>');

        $popupBody.append($loading);

        // dynamically load the leaderboard
        $.ajax({
            url: '/gamification/badge-collection/',
            type: 'GET',
            success: function(data) {
                $popupBody.html(data);
            }
        })
    });
});