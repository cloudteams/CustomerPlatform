webpackJsonp([2,8],[
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	'use strict';

	var _CustomerIdeas = __webpack_require__(1);

	var _CustomerIdeas2 = _interopRequireDefault(_CustomerIdeas);

	function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

	(function () {
		function start() {
			_CustomerIdeas2.default.run();
		}

		$(document).ready(function () {
			start();
		});
	})();

/***/ },
/* 1 */
/***/ function(module, exports) {

	'use strict';

	Object.defineProperty(exports, "__esModule", {
		value: true
	});

	exports.default = function () {
		function openElement(element, element2) {
			var curHeight = element.height();
			var autoHeight = element.css('height', 'auto').height();

			element.height(curHeight).addClass('extended').animate({
				'height': autoHeight
			}, 0, 'easeInOutCirc', function () {
				element.addClass('active');
			});

			if (element2) {
				element2.removeClass('angle-closed').addClass('angle-open');
			}
		}

		function closeElement(element, element2) {
			var initialHeight = '0px';

			element.removeClass('extended').animate({
				'height': initialHeight
			}, 0, 'easeInOutCirc', function () {
				setTimeout(function () {
					element.removeClass('active');
				}, 300);
			});

			if (element2) {
				element2.removeClass('angle-open').addClass('angle-closed');
			}
		}

		function openCloseElement(element) {
			var content = element.find('.content');
			var angle = content.prev('.fa-angle-right');

			if (!content.hasClass('extended')) {
				openElement(content, angle);
			} else {
				closeElement(content, angle);
			}
		}

		function runOpenCloseElement() {
			var idea = $('.idea .idea-container');

			idea.click(function () {
				openCloseElement($(this));
			});
		}

		function like(element) {
			if (!element.hasClass('active')) {
				element.addClass('active');
			} else {
				element.removeClass('active');
			}
		}

		function runLikeButton() {
			var likeButton = $('.like-button');

			likeButton.click(function () {
				like($(this));
			});
		}

		function run() {
			runOpenCloseElement();
			runLikeButton();
		}

		return {
			run: run
		};
	}();

/***/ }
]);