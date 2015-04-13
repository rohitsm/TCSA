
// Save email to browser's session storage on button click
function (){
	$('#myModal').modal('show');
	// alert("The TCSA Chrome plugin is currently being reviewed by the Chrome Web Store. Please try again in a few days.");
};

window.onload = function() {
	sessionStorage.setItem("Email_ls", email);
};