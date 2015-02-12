$(document).ready(function(){
	$("#fileRegion").hide();
	$("#upload").click(function(){
		$("#download").hide();
		$("#fileRegion").show();
		var fileInput=document.getElementById("fileInput");
		var encrypt=document.getElementById("encrypt");
		var count;
		var file=[];

		fileInput.addEventListener('change', function(e) {
			/*count=fileInput.files.length;
			alert("count "+ count);
			for(var i=0; i<count; i++){
				file=fileInput.files;
				
			}*/
			file=fileInput.files;

		});
		encrypt.addEventListener('click',function(e){
			for(var i=0;i<count;i++){
				alert("i"+i);
				encryptFileProcess(file[i]);
			}
			//encryptFileProcess(file);

			
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