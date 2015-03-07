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
			url	: "http://127.0.0.1:5000/testajax",
			// url	: "/login1",
			type: "POST",
			data: { 'Email' : email,
					'Password': password
			},
			contentType: "application/x-www-form-urlencoded; charset=UTF-8", 
			crossOrigin: true,
			success : 	function(response, textStatus, jqXHR) {
							alert_msg = "Success";
							console.log("Success: " + jqXHR.responseText + ' ' + jqXHR.status );
							var email = JSON.parse(jqXHR.responseText)['email'];
							console.log("jsonResponse = " + jsonResponse);
							document.write(response);

							// window.location = "login2.html"

							// top.location.href = 'https://155.69.145.226/login1'
							// $("#alert").html(
							// 	'<div class="alert alert-success text-center">' +
							// 		'<span class="glyphicon glyphicon-exclamation-sign">' + alert_msg + '</span>' + 
							// 	'</div>'
							// );
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
