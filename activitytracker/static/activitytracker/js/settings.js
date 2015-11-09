/**
 * Created by Aggelos.
 *
 */


	function synchronizeProvider(provider){
			Loading();
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
					Done();
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
					url: '/disconnect/' + provider,
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

