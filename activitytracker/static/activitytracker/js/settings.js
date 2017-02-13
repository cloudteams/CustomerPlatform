/**
 * Created by Aggelos.
 *
 */


	function synchronizeProvider(provider, button){

			var $button = $(button);
			var width = $button.css('width')
			$button.html('<i class="fa fa-spinner fa-spin spinner margin-right-1"></i>Syncing...');

			$.ajax({
				type: "post",
				data: {csrfmiddlewaretoken: getCookie('csrftoken')},
				cache: false,
				url: BASE_URL + "settings/sync/" +  provider +'/',
				dataType: "text",
				error: function (xhr, status, error) {
					alert(xhr.responseText);
					Done();
				},
				success: function (response) {

					$button.html('Synchronize');
					$('#success-msg').removeClass('hidden').text(response);
					if ($('.' + provider + ' .connected-app-button').length == 1) {
						setTimeout(function(){ window.location.reload(); }, 3000);
					}

				}
			});
		}


        function appFunctionHandler(provider, button_clicked) {
			if ($(button_clicked).attr('title') == "De-Authorize") {
				LoadingWithBackdrop();
				$.ajax({
					type: "post",
					data: {csrfmiddlewaretoken: getCookie('csrftoken')},
					cache: false,
					url: '/disconnect/' + provider + '/',
					dataType: "text",
					error: function (xhr, status, error) {
						alert("Couldn't disconnect, try again")
					},
					success: function (response) {
						window.location.reload();
					}
				});
			}
			else if ($(button_clicked).attr('title') == "Retry") {
				window.location.reload();
			}
			else {
				var url = "/login/" + provider + '?next=' + BASE_URL + 'social_login/sync/' + provider;
				window.open(url, 'newwindow', 'width=500, height=500')
			}
		}

		/* On email notification settings change */
		$('#email-notifications-settings').on('change', function() {
			var $message = $(this).parent().find('.message'),
				$csrf = $(this).parent().find('input[name="csrfmiddlewaretoken"]'),
				status = $(this).val();

			$message.html('<div class="loader-general loader-general-gray"></div><span style="vertical-align: top;padding-top: 10px;margin-left: 10px;display: inline-block;color: #aaa;">Updating your settings...</span>');

			/* update settings */
			$.ajax({
				url: '/profile/settings/email-notifications/',
				type: 'POST',
				data: {
					csrfmiddlewaretoken: $csrf.val(),
					status: status
				},
				success: function() {
					$message.html('<i class="fa fa-check"></i> Email notifications are now <b>' + status + '</b>.');
				},
				error: function() {
					$message.html('<i class="fa fa-times"></i> Some error occurred. Please try again later.');
				}
			});
		});

