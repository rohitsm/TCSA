$(document).ready(function(){
	$("#password").focus();
	$("#generator").click(function(){
		var score=0;
		var strength=["Weak","Medium","Strong","Very Strong"];
		var passBox= document.getElementById("password");
		var password=passBox.value;
		if(password.length<6){
			alert("Your password is too short please key in again");
			passBox.value="";
			passBox.focus();
		}
		else{
			//if txtpass has both lower and uppercase characters give 1 point
     		if ( ( password.match(/[a-z]/) ) && ( password.match(/[A-Z]/) ) ) score++;

		     //if txtpass has at least one number give 1 point
		     if (password.match(/\d+/)) score++;

		     //if txtpass has at least one special caracther give 1 point
		     if ( password.match(/.[!,@,#,$,%,^,&,*,?,_,~,-,(,)]/) ) score++;

		     //if txtpass bigger than 12 give another 1 point
		     if (password.length > 12) score++;

		     if(score<2){
		     	alert("Your Password is weak for the Key Generation");
		     	passBox.value="";
				passBox.focus();
		     }
		     else{
		     	hashedTxt=Sha256.hash(password);
		     	passBox.value="";
		     	alert(hashedTxt);
		     	//document.cookie="password="+hashedTxt;
		   		sessionStorage.setItem("password",hashedTxt);
		   		window.location="viewer.html";
		     }
		}
	});
});

