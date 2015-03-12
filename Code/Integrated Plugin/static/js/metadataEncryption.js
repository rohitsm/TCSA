/***************
var metadata=localStorage.getItem("metadata");
encryptMetadata(metadata);
the logout button click event call the encrypt metadata
take the metadata from localStorage
encryption is the same as file encryption
***************/


var count=count2=0;
var ciphertext="";
var password="appa1234";

function encryptMetadata(metadata){
	count=count2=0;
	var blobs = [];
	buf=metadata;
	//buf= new Uint8Array((Object)metadata); //load file bytes to buffer
	for (var i = 0; i < buf.length; i += 1e6){
		blobs.push(new Blob([buf.substring(i, i + 1e6)]));
		count++;
	}
	encryptMeta(blobs);
};

function encryptMeta(blobs){
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
				encryptMeta(e);
			}
			
			reader.onprogress = function() {          
                var progress = parseInt( (count2+1) / count * 100);
				$('#progressbar').val(progress);
                console.log(progress);
            }
        
		}
		else{
			alert("ciphertext metadata= "+ciphertext);
		    //ciphertext="";
		    useremail="admin@tcsa.com";//localStorage.getItem("username");
		    uploadMetadata(useremail,ciphertext);
		}			
}


//upload to the server by the request upload_metadata
function uploadMetadata(useremail,ciphertext){

      data= { 
      	'req': 'upload_metadata',
		'user_email': useremail,
		'metadata': ciphertext
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
          alert(status);
          if(status=='OK'){
            //str=encryptedMetadata;
            str = alert(JSON.parse(jqXHR.responseText)['user_email']);  
            localStorage.removeItem("metadata");
            localStorage.removeItem("password");
            localStorage.removeItem("path");
            localStorage.removeItem("filename");
            sessionStorage.removeItem("Email_ls");
            sessionStorage.removeItem("password");
            alert("Successfully logged out");
            window.location="test.html";
          }
          else{
            alert("error");
            window.location="index.html";
          }
        },    
        error: function(response,error) {
          alert("ERROR");
          window.location="index.html";
        }
      });
}