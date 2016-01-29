webpackJsonp([3,8],[
/* 0 */
/***/ function(module, exports) {

	'use strict';

	(function () {
		function openItem(item) {
			item.removeClass('passive').addClass('active');
		}

		function closeItem(item) {
			item.removeClass('active').addClass('passive');
		}

		function active(item) {
			item.addClass('active');
		}

		function passive(item) {
			item.removeClass('active');
		}

		function openCloseComment(element) {
			var currentLinkID = parseInt(element.attr('id').replace(/[^\d]/g, ''), 10);
			var currentMessageComments = $('#comments-message-' + currentLinkID);

			if (!currentMessageComments.hasClass('active')) {
				openItem(currentMessageComments);
				active(element);
			} else {
				closeItem(currentMessageComments);
				passive(element);
			}
		}

		function runOpenCloseComment() {
			var commentTrigger = $('.comment-trigger');

			commentTrigger.click(function () {
				openCloseComment($(this));
			});
		}

		function like(element) {
			if (!element.hasClass('active')) {
				active(element);
			} else {
				passive(element);
			}
		}

		function runLikeButton() {
			var likeButton = $('.like-button');

			likeButton.click(function () {
				like($(this));
			});
		}

		$(document).ready(function () {
			runOpenCloseComment();
			runLikeButton();
		});
	})();

/***/ }
]);