var blobs = [];
var count=count2=0;
var plaintext="";
var contentBytes=[];
var password="appa1234";//localStorage.getItem("password");
var file;
var newstr='';

function download(useremail,filename){
      data= { 
      		'req': 'download',
		    'user_email': useremail,
		    'filename':filename
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
            str = JSON.parse(jqXHR.responseText)['file_content'];  
			decryptFileProcess(str);
          }
          else{
            alert("Success but error");
            window.location="index.html";
          }
        },    
        error: function(jqXHR,textStatus,error) {
        	console.log("error" + jqXHR.status + " " + textStatus + " " + jqXHR.responseText + " " + error);
        	window.location="index.html";
        }
      });
}

function decryptFileProcess(str){
	  var str=str; //load file bytes to buffer
	  var buf=str.split("-");
	  
		for (var i = 0; i < buf.length-1; i++){
	    	blobs.push(new Blob([buf[i]]));
	    	count++;
	    }
	decryptFile();
}

// function decryptFileProcess(file){
// 	var fr = new FileReader();
// 	fr.readAsText(file);
	
// 	fr.onload = function(e) {
// 	  var str=e.target.result; //load file bytes to buffer
// 	  var buf=str.split("-");
	  
// 		for (var i = 0; i < buf.length-1; i++){
// 	    	blobs.push(new Blob([buf[i]]));
// 	    	count++;
// 	    }
// 	};
// 	decryptFile();
// }

function decryptFile(e){
		console.log("Part "+ (count2+1) + " of "+ count);
		if(count2<count){
			var reader = new FileReader();
    		reader.readAsText(blobs[count2]);
    		reader.onload = function(evt) {
    			var content = reader.result;
		        plaintext += Aes.Ctr.decrypt(content, password, 256);
			}
			reader.onloadend= function(evt){
				count2=count2+1;
				decryptFile(evt);
			}
		}
		else{

				contentBytes = new Uint8Array(plaintext.length);
		        for (var i=0; i<plaintext.length; i++) {
		            contentBytes[i] = plaintext.charCodeAt(i);
		        }

				var blob = new Blob([contentBytes], { type: 'application/octet-stream' });
				var filename= localStorage.getItem("filename");
			    saveAs(blob, filename);
			    plaintext="";
			    window.location="index.html";
		}
				
}



