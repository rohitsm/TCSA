
var count=count2=0;
var ciphertext="";
var password=localStorage.getItem("password");
//fileInput.addEventListener('change', function(e) {
	function encryptFileProcess(file){
		var blobs = [];
		//file=fileInput.files[0];
		var fr = new FileReader();
		var buf;
		var filename = file.name+'.encrypted';
		fr.onload = function(e) {
		  buf= new Uint8Array(e.target.result); //load file bytes to buffer
		  	
			for (var i = 0; i < buf.length; i += 1e6){
		    	blobs.push(new Blob([buf.subarray(i, i + 1e6)]));
		    	count++;
		    }
		};
		fr.readAsArrayBuffer(file);

		fr.onloadend = function(e){
			alert("2:" +blobs);	
			encryptFile(blobs,filename);
		}
	//	

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
			var blob = new Blob([ciphertext], { type: 'text/plain' });
		    saveAs(blob, filename);
			//upload(blob, filename);
		}
		
				
}

function upload (blob, filename) {

      var url = (window.URL || window.webkitURL).createObjectURL(blob);
      console.log(url);

     // var filename = <?php echo $filename;?>;
      var data = new FormData();
      data.append('file', blob);

      $.ajax({
        url :  "http://127.0.0.1:5723/upload.php",
        type: 'POST',
        data: data,
        contentType: false,
        processData: false,
        success: function(data) {
          alert("boa!" + data);
        },    
        error: function() {
          alert("not so boa!");
        }
      });
} 

