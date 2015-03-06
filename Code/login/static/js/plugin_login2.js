// AJAX for POSTing

console.log("hello2");

$(document).ready(function(){
	// Retrieve email from browser's session storage
	var local_email = sessionStorage.getItem("Email_ls");
	if (local_email == null){
		alert('Invalid email or password!');
		window.location = "test.html";

	}
	console.log(local_email);	
	$("input#Email").val(local_email);
	console.log("inside");
	
	// 	'<div class="alert alert-success text-center">' +
	// 		'<span class="glyphicon glyphicon-exclamation-sign">' + alert_msg + '</span>' + 
	// 	'</div>'
	// );

	$("form#login_form").submit(function(event){
		console.log("Hello World2!");
		var passphrase = $("input#Passphrase").val();
		console.log(local_email + passphrase);
		event.preventDefault();
		console.log("Was preventDefault() called: " + event.isDefaultPrevented());
		
		$.ajax ({
			// url	: "https://cloudstag.me/testajax2",

			url	: "https://cloudstag.me/testajax2",
			type: "POST",
			data: { 'Email' : local_email,
					'Passphrase': passphrase
			},
			contentType: "application/x-www-form-urlencoded; charset=UTF-8", 
			crossOrigin: true,
			xhrFields: {
						withCredentials: false
						},
			success : 	function(response, textStatus, jqXHR) {
							alert_msg = "Success";
							console.log("Success: " + jqXHR.responseText + ' ' + jqXHR.status );
							var status = JSON.parse(jqXHR.responseText)['status'];
							if (status == "OK"){
								console.log("Status: " + status);
								var email = JSON.parse(jqXHR.responseText)['email'];
								console.log("email = " + email);
								document.write(response);
								window.location = "viewer.html"
						}

						console.log("Error!");
						window.location = "test.html"

						// top.location.href = 'https://155.69.145.226/login1'
						$("#alert").html(
							'<div class="alert alert-success text-center">' +
								'<span class="glyphicon glyphicon-exclamation-sign">' + alert_msg + '</span>' + 
							'</div>'
						);
						},

			error 	:	function(jqXHR, textStatus, errorThrown) {
							alert_msg = "Incorrect email or password!";							
							console.log("error: " + jqXHR.status + " " + textStatus + ' ' + jqXHR.responseText + ' ' + errorThrown);
							$("#alert").html(
								'<div class="alert alert-danger text-center">' +
									'<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true">'+ alert_msg +'</span>' + 
								'</div>'
							);
						} 

		}); //Ajax
		// $("#login_form")[0].reset();
	}); //submit
});
