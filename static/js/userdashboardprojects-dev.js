webpackJsonp([7,8],[
/* 0 */
/***/ function(module, exports) {

	'use strict';

	(function () {
		function closeItem(item) {
			item.removeClass('active');
		}

		function openClose(element) {
			var message = element.parent().parent();
			var dashboard = $('.dashboard-page');

			if (message.hasClass('active')) {
				closeItem(message);
				dashboard.addClass('top');
			}
		}

		function runOpenClose() {
			var close = $('.close-message');

			close.click(function () {
				openClose($(this));
			});
		}

		function openTutorial() {
			var userTutorial = $('#popup-tutorial-user');

			userTutorial.modal('show');
		}

		$(document).ready(function () {
			runOpenClose();
			openTutorial();
		});
	})();

/***/ }
]);