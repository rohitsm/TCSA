// AJAX for POSTing

console.log("hello");

$(document).ready(function(){
	$("form#login_form").submit(function(event){
		console.log("Hello World!");
		var email = $("input#Email").val();
		var password = $("input#Password").val();
		console.log(email + password);
		event.preventDefault();
		console.log("Was preventDefault() called: " + event.isDefaultPrevented());
		
		$.ajax ({
			url	: "https://cloudstag.me/testajax",
			type: "POST",
			data: { 'Email' : email,
					'Password': password
			},
			contentType: "application/x-www-form-urlencoded; charset=UTF-8", 
			crossOrigin: true,
			xhrFields: {
						withCredentials: false
						},

			success : 	function(response, textStatus, jqXHR) {
							// alert_msg = "Success";
							console.log("Success: " + jqXHR.responseText + ' ' + jqXHR.status );
							var status = JSON.parse(jqXHR.responseText)['status'];
							console.log("Status: " + status);
							if (status == "OK"){
								var email_resp = JSON.parse(jqXHR.responseText)['email'];
								console.log("email_resp = " + email_resp);

								// DEBUG
								document.write(response);
								// Save email to browser's session storage
								sessionStorage.setItem("Email_ls", email_resp);								
								window.location = "test2.html";
							}
							else{
								alert('Invalid email or password!');
								window.location = "test.html";
								$("#login_form")[0].reset();
								alert_msg = "Incorrect email or password!";							
								console.log("error: " + jqXHR.status + " " + textStatus + ' ' + jqXHR.responseText );
								$("#alert").html(
									'<div class="alert alert-danger text-center">' +
										'<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true">'+ alert_msg +'</span>' + 
									'</div>'
								);
								// DEBUG
								// document.write(response);								
							}
						}, // success

			error 	:	function(jqXHR, textStatus, errorThrown) {
							alert_msg = "Woah horsey! Something's not right!";						
							console.log("error: " + jqXHR.status + " " + textStatus + ' ' + jqXHR.responseText + ' ' + errorThrown);
							$("#alert").html(
								'<div class="alert alert-danger text-center">' +
									'<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true">'+ alert_msg +'</span>' + 
								'</div>'
							);
							$("#login_form")[0].reset();
						} 

		}); //Ajax
		// $("#login_form")[0].reset();
	}); //submit
});

