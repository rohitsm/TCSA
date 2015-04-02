/***************
encrypting the file uploaded
read file with filereader change UINT8ARRAY 
split up the large file to different smaller blobs
encrypting the data
encrypt and salt the file name
***************/

var flag=0;
var count=count2=0;
var ciphertext="";
var password=sessionStorage.getItem("password");

var curPath;
var metadata;

function encryptFileProcess(file){
	curPath=localStorage.getItem("path");
	metadata=localStorage.getItem("metadata");
	curPath+="/"+file.name;
	//alert(curPath);
	metadata+="\n"+ curPath;
	count=count2=0;
	var blobs = [];
	//file=fileInput.files[0];
	var fr = new FileReader();
	var buf;
	var filename = file.name;
	
	var aa = fr.readAsArrayBuffer(file);
	fr.onloadstart = function(e){
		
	}
	fr.onload = function(e) {
	  buf= new Uint8Array(e.target.result); //load file bytes to buffer
	  
	  for (var i = 0; i < buf.length; i += 1e6){
	  	blobs.push(new Blob([buf.subarray(i, i + 1e6)]));
	  	count++;
	  }
	};
	

	fr.onloadend = function(e){
		encryptFile(blobs,filename);

	}
}

//calling AES counter encryption
function encryptFile(blobs,filename){
		if(count2<count){
			console.log("Part "+ (count2+1) + " of "+ count);
			var reader = new FileReader();
    		reader.readAsArrayBuffer(blobs[count2]);

    		reader.onload = function(evt) {
			
        		var contentBytes = new Uint8Array(reader.result); // ≡ evt.target.result
        		var contentStr = '';
        		for (var i=0; i<contentBytes.length; i++) {
            		contentStr += String.fromCharCode(contentBytes[i]);
        		}
        		//alert(contentStr);
        		ciphertext +=Aes.Ctr.encrypt(contentStr, password, 256)+"-";
        		
				
			}
			reader.onloadend=function(e){
				count2=count2+1;
				encryptFile(blobs,filename);
			}
			
			reader.onprogress = function() {          
                var progress = parseInt( (count2+1) / count * 100);
				$('#progressbar').val(progress);
                console.log(progress);
            }
        
		}
		else{
			var currentPath=localStorage.getItem("path");
			filename= currentPath+"/"+filename;
			filename = password.substring(0,10) + filename ; 
   			filename = Sha256.hash(filename); 
			var blob = new Blob([ciphertext], { type: 'text/plain' });
			var username=sessionStorage.getItem("Email_ls");
		    //saveAs(blob, filename);
		    upload(ciphertext, filename,username);
		    ciphertext="";
		    next++;
		    //alert("Calling encrypt");
		    //callEncrypt();
		}
}

//upload to the server after encryption
function upload (ciphertext, filename,username) {
		alert("user_email "+username+"\npassword "+password);
      data= {
			'req': 'upload',
			'user_email': username,
			'filename': filename,
			'file_content': ciphertext
		}

      $.ajax({
        url :  "https://cloudstag.me/testupload",
        type: 'POST',
        data: JSON.stringify(data, null, '\t'),
        contentType: 'application/json;charset=UTF-8',
        crossOrigin: true,
        xhrFields: {
        	withCredentials: false
        },
        success: function(repsonse,textStatus, jqXHR) {
          var status= JSON.parse(jqXHR.responseText)['status'];
          if(status=='OK'){
          	alert("OK"+JSON.parse(jqXHR.responseText)['user_email']);
          	localStorage.setItem("metadata",metadata);
          	window.location= "index.html";
          }
          else{
          	alert("Error");
          	localStorage.setItem("metadata",metadata);
            window.location="index.html"; 
          }
        },    
        error: function(response,error) {
          alert("ERROR");
        }
      });
} 

