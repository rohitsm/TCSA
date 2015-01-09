// Write email to browser's local session storage

function setEmail_ls(email){
	// Save email to browser's session storage on button click
	console.log("Email: ")
	console.log(email)
	sessionStorage.setItem("Email_ls", email);
}
