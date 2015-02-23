var flag=0;
var count=count2=0;
var ciphertext="";
var password=localStorage.getItem("password");
//fileInput.addEventListener('change', function(e) {
	function encryptFileProcess(file){
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
				encryptFile(e,filename);
			}
			
			reader.onprogress = function() {
                                                   
                var progress = parseInt( (count2+1) / count * 100);
				$('#progressbar').val(progress);
                console.log(progress);
            }
        
		}
		else{
			alert(filename);
			filename = password.substring(0,10) + filename ; //+ lalalaa :D salting to be done
        	//filename = Aes.cipher(filename,password);
   			filename = Aes.Ctr.encrypt(filename, password, 256);
			var blob = new Blob([ciphertext], { type: 'text/plain' });
		    saveAs(blob, filename);
		    //upload(ciphertext, filename);
		    ciphertext="";
		    next++;
		    //alert("Calling encrypt");
		    //callEncrypt();
			
		}
		
				
}

function upload (ciphertext, filename) {

      //var url = (window.URL || window.webkitURL).createObjectURL(blob);
      //console.log(url);

     // var filename = <?php echo $filename;?>;
      //var blobdata = new FormData();
      //blobdata.append('file', blob);
      //alert(blobdata);
     
      data= { 'filename' : filename,
  			'file_content': ciphertext
  			//'user': //to be added when i got username
  			}
      $.ajax({
        url :  "https://155.69.145.226/testupload",
        type: 'GET',
        data: JSON.stringify(data, null, '\t'),
        contentType: 'application/json;charset=UTF-8',
        processData: false,
        success: function(data) {
          alert("Successful!");
        },    
        error: function(response,error) {
          alert("ERROR");
        }
      });
} 

