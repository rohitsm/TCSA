var next=0;
var previous=1;
$(document).ready(function(){
	$("#fileRegion").hide();
	$("#upload").click(function(){
		//window.location="filedisplay.html";
		$("#upload").hide();
		$("#fileRegion").show();
		var fileInput=document.getElementById("fileInput");
		var encrypt=document.getElementById("encrypt");
		var count;
		var file=[];

		fileInput.addEventListener('change', function(e) {
			count=fileInput.files.length;
			alert("count "+ count);
			/*for(var i=0; i<count; i++){
				file=fileInput.files;
				
			}*/
			file=fileInput.files;
		});
		encrypt.addEventListener('click',function(e){
			var curPath=localStorage.getItem("path");
			var metadata=localStorage.getItem("metadata");
			while(next<count && next!=previous){
				previous=next;
				alert("next"+next);
				encryptFileProcess(file[next]);
				curPath+="/"+file[next].name;
				alert(curPath);
				metadata+="\n"+ curPath;
			}
			//encryptFileProcess(file);
			localStorage.setItem("metadata",metadata);
			window.location="index.html";
			
		});
	});

	/*$("#download").click(function(){
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

	});*/
});