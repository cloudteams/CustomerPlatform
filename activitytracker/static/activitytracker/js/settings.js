/**
 * Created by Aggelos.
 *
 */

	/* for account delete */
	//$("#deleteaccountForm").submit(function(event) {
	//	event.preventDefault();
	//	var pass = document.forms["deleteaccountForm"]["password"].value;
	//	Loading();
	//	$.ajax({
	//		type: "post",
	//		data: {password:pass, settingAction:'deleteaccount', csrfmiddlewaretoken: getCookie('csrftoken')},
	//		cache: false,
	//		url: BASE_URL + "settings/",
	//		dataType: "text",
	//		error: function (xhr, status, error) {
	//			Done();
	//			$('#deleteaccountmsg').text(xhr.responseText);
	//		},
	//		success: function (response) {
	//			window.location.replace(BASE_URL + "login/");
	//		}
	//	});
	//});

	/* for info edit */
	//$("#editinfoForm").submit(function(event) {
	//	$('#editfailmsg').text('');
	//	event.preventDefault();
	//	Loading();
	//	var data = {
	//		username: document.forms["editinfoForm"]["username"].value,
	//		firstname: document.forms["editinfoForm"]["firstname"].value,
	//		lastname: document.forms["editinfoForm"]["lastname"].value,
	//		email: document.forms["editinfoForm"]["email"].value,
	//		birthday: document.forms["editinfoForm"]["birthday"].value,
	//		gender: document.forms["editinfoForm"]["gender"].value,
	//		settingAction: 'editinfo',
	//		csrfmiddlewaretoken: getCookie('csrftoken')
	//	};
	//	$.ajax({
	//		type: "post",
	//		data: data,
	//		cache: false,
	//		url: BASE_URL + "settings/",
	//		dataType: "json",
	//		error: function (xhr, status, error) {
	//			Done();
	//			$('#editinfomsg').text(xhr.responseText);
	//		},
	//		success: function (response) {
	//			$('#Tblusername').text(response.username);
	//			$('#Tblfirstname').text(response.fname);
	//			$('#Tbllastname').text(response.lname);
	//			$('#Tblemail').text(response.email);
	//			$('#Tblbirth').text(response.birthday);
	//			$('#Tblgender').text(response.gender);
	//			$('#successmsg').text('Information updated successfully!');
	//			$('#username').text(response.username);
	//			Done();
	//			$('#editinfo').modal('hide');
    //
	//		}
	//	});
	//});

	/* for password change*/
	//$("#passchangeForm").submit(function(event) {
	//	event.preventDefault();
	//	var data = {
	//		old_password: document.forms["passchangeForm"]["old_password"].value,
	//		new_password: document.forms["passchangeForm"]["new_password"].value,
	//		new_password_repeat: document.forms["passchangeForm"]["new_password_repeat"].value,
	//		settingAction: 'passchange',
	//		csrfmiddlewaretoken: getCookie('csrftoken')
	//	};
	//	$.ajax({
	//		type: "post",
	//		data: data,
	//		cache: false,
	//		url: BASE_URL + "settings/",
	//		dataType: "text",
	//		error: function (xhr, status, error) {
	//			Done();
	//			$('#passchangemsg').text(xhr.responseText);
	//		},
	//		success: function (response) {
	//			Loading();
	//			$('#successmsg').text('Password changed successfully!');
	//			$('#changepassword').modal('hide');
	//			setTimeout(function(){
	//				window.location = BASE_URL + "login/";
	//				Done();
	//			}, 3000);
	//		}
	//	});
	//});


	//$('#changepassword').on("hidden", function () {
	//	$('#passchangemsg').text('');
	//	document.getElementById("passchangeForm").reset();
	//});
	//$('#deleteaccount').on("hidden", function () {
	//	$('#deleteaccountmsg').text('');
	//	document.getElementById("deleteaccountForm").reset();
	//});
	//  $('#editinfo').on("hidden", function () {
	//	$('#editinfomsg').text('');
    //
	//});
	//$('.modal').on("shown", function () {
	//	$('#successmsg').html("&nbsp;");
	//});

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
					alert(response);

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

