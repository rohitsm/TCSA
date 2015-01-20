/* Form validation */

function validateEmail() {
	/* Checks the general syntax of email:
		- Input data must contain an '@' sign and atleast one dot (.)
		- '@' must not be the first character of the email
		- Last dot (.) must be present after the '@' and 2 chars before the end
	*/
	var eml = document.forms["signupForm"]["Email"].value;
	var atpos = eml.indexOf("@");
	var dotpos = eml.lastIndexOf(".");
	if (atpos < 1 || dotpos < atpos+2 || dotpos + 2 >= eml.length){
		alert("Not a valid e-mail address!");
		document.forms["signupForm"]["Email"].focus();
		return false;
	}
	return true;
}

function validatePwd1(){
	/* Check if the password has min length = 8	and is not null */
	
	var pwd1 = document.forms["signupForm"]["Password1"].value;
	if (pwd1.length < 5){
		alert("Password must have minimum 5 characters!")
		document.forms["signupForm"]["Password1"].focus();
		return false;
	}
}

function validatePwd() {
	/* 	Check if the two passphrases match */

	var pwd1 = document.forms["signupForm"]["Password1"].value;
	var pwd2 = document.forms["signupForm"]["Password2"].value;
	if (pwd1 != pwd2){
		alert("Passwords don't match!")
		document.forms["signupForm"]["Password1"].focus();
		return false;
	}  
	return true;
}

function validatePassph1(){
	/* Check if the passphrase has min length = 8	and is not null */

	var pps1 = document.forms["signupForm"]["Passphrase1"].value;
	if (pps1.length < 8){
		alert("Passphrase must have minimum 5 characters!")
		document.forms["signupForm"]["Passphrase1"].focus();
		return false;
	}
}

function validatePassphrase() {
	/* 	Check if the two passphrases match */

	var pps1 = document.forms["signupForm"]["Passphrase1"].value;
	var pps2 = document.forms["signupForm"]["Passphrase2"].value;

	if (pps1 != pps2){
		alert("Passphrases don't match!")
		document.forms["signupForm"]["Passphrase1"].focus();
		return false;
	}  
	return true;
}


function validateForm() {
	return !!(validateEmail() && validatePwd() && validatePassphrase());
}