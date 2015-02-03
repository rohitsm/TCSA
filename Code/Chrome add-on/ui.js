$(document).ready(function(){
	$("#fileRegion").hide();
	$("#upload").click(function(){
		$("#download").hide();
		$("#fileRegion").show();
		var fileInput=document.getElementById("fileInput");
		var encrypt=document.getElementById("encrypt");
		fileInput.addEventListener('change', function(e) {
			file=fileInput.files[0];
			encryptFileProcess(file);
		});
		encrypt.addEventListener('click',function(e){
			encryptFile(e);
		});
	});

	$("#download").click(function(){
		$("#upload").hide();
		$("#fileRegion").show();
		var fileInput=document.getElementById("fileInput");
		var decrypt=document.getElementById("encrypt");
		decrypt.innerText="Decrypt";
		fileInput.addEventListener('change', function(e) {
			file=fileInput.files[0];
			decryptFileProcess(file);
		});

		decrypt.addEventListener('click',function(e){
			decryptFile(e);
		});

	});
});