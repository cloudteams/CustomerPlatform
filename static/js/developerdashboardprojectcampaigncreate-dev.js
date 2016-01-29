webpackJsonp([0,8],[
/* 0 */
/***/ function(module, exports) {

	'use strict';

	(function () {
		function activeSubMenuItem() {
			var navLink = $('.side-menu > ul > li a[href="developer-dashboard-project-campaigns.php"]');

			navLink.addClass('active');
		}

		$(document).ready(function () {
			activeSubMenuItem();
		});
	})();

/***/ }
]);