var blobs = [];
var count=count2=0;
var ciphertext="";
var password="appa";

//fileInput.addEventListener('change', function(e) {
	function encryptFileProcess(file){
		//file=fileInput.files[0];
		var fr = new FileReader();
		var buf;
		
		fr.onload = function(e) {
		  buf= new Uint8Array(e.target.result); //load file bytes to buffer
		  
			for (var i = 0; i < buf.length; i += 1e6){
		    	blobs.push(new Blob([buf.subarray(i, i + 1e6)]));
		    	count++;
		    	
		    	//filedisplay.innerText= CryptoJS.AES.encrypt(e.target.result, "appaa");
		    }
		};
		fr.readAsArrayBuffer(file);
	}


function encryptFile(e){
		if(count2<count){
			var reader = new FileReader();
    		reader.readAsArrayBuffer(blobs[count2]);

    		reader.onload = function(evt) {
        		var contentBytes = new Uint8Array(reader.result); // ≡ evt.target.result
        		var contentStr = '';
        		for (var i=0; i<contentBytes.length; i++) {
            		contentStr += String.fromCharCode(contentBytes[i]);
        		}
        		ciphertext +=Aes.Ctr.encrypt(contentStr, password, 256)+"-";
				count2=count2+1;

				
			}
		}
		else{
			var blob = new Blob([ciphertext], { type: 'text/plain' });
		    var filename = file.name+'.encrypted';
		    saveAs(blob, filename);
		}
		
				
}

