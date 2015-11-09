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

				}
			});
		}


        function appFunctionHandler(provider) {
			if ($('.' + provider + ' .connected-app-button').text() == "SynchronizeDisconnect") {
				LoadingWithBackdrop();
				$.ajax({
					type: "post",
					data: {csrfmiddlewaretoken: getCookie('csrftoken')},
					cache: false,
					url: SERVER_URL + '/disconnect/' + provider,
					dataType: "text",
					error: function (xhr, status, error) {
						alert("Couldn't disconnect, try again")
					},
					success: function (response) {
						window.location.reload();
					}
				});
			}
			else if ($('.' + provider + ' .connected-app-button').text() == "Try again") {
				window.location.reload();
			}
			else {
				var url = (SERVER_URL + "/login/" + provider);
				window.open(url, 'newwindow', 'width=500, height=500')
			}
		}

