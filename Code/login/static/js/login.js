
// AJAX for POSTing
var email;
var pwd;
console.log("Hello World!");

$(document).ready(function (){
	$("#Submit2").click(function() {
		email = $('#Email').val();
		pwd = $('#Password').val();

		$.ajax ({
			// url	: "https://cloudstag.me/login1",
			url	: "/testajax",
			type: "POST",
			data: { email : $('#Email').val(),
					password: $('#Password').val()
			},
			contentType: "application/x-www-form-urlencoded; charset=UTF-8", 

			success : function(data){
				alert("Success");
			},

			error: function(response){
				alert("Error");
			}
		});

		// DEBUG
		console.log(email);
		console.log(pwd);

	});

});

alert('Works');

// alert_msg = message[1]

// if (message[0] == "success"){ // Correct 
// 	$(document).ready(function(){
// 		$("#alert").html(
// 			'<div class="alert alert-success text-center">' +
// 				'<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true">' + alert_msg + '</span>' + 
// 			'</div>');
// 		});	
// }
// else if (message[0] == "error" ) {
// 	$(document).ready(function(){
// 		$("#alert").html(
// 			'<div class="alert alert-danger text-center">' +
// 				'<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true">'+ alert_msg +'</span>' + 
// 			'</div>');
// 		});
// }