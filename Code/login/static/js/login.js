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
			url	: "https://cloudstag.me/login1",
			// url	: "/login1",
			type: "POST",
			data: { 'Email' : email,
					'Password': password
			},
			contentType: "application/x-www-form-urlencoded; charset=UTF-8", 
			success : 	function(response) {
							alert_msg = "Success";
							// console.log("Success: " + textStatus + ' ' + jqXHR);
							document.write(response);
							// $("#alert").html(
							// 	'<div class="alert alert-success text-center">' +
							// 		'<span class="glyphicon glyphicon-exclamation-sign">' + alert_msg + '</span>' + 
							// 	'</div>'
							// );
						},

			error 	:	function(jqXHR, textStatus, errorThrown) {
							alert_msg = "Incorrect email or password!";							
							console.log("error: " + textStatus + ' ' + jqXHR + ' ' + errorThrown);
							$("#alert").html(
								'<div class="alert alert-danger text-center">' +
									'<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true">'+ alert_msg +'</span>' + 
								'</div>'
							);
						} 

		}); //Ajax
		$("#login_form")[0].reset();
	}); //submit
});