alert('Works')
alert_msg = message[1]

if (message[0] == "success"){ // Correct 
	$(document).ready(function(){
		$("#alert").html(
			'<div class="alert alert-success text-center">' +
				'<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true">' + alert_msg + '</span>' + 
			'</div>');
		});	
}
else if (message[0] == "error" ) {
	$(document).ready(function(){
		$("#alert").html(
			'<div class="alert alert-danger text-center">' +
				'<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true">'+ alert_msg +'</span>' + 
			'</div>');
		});
}