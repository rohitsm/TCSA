var count=count2=0;
var ciphertext="";
var password="appa1234";
//var metadata=localStorage.getItem("metadata");
//encryptMetadata(metadata);
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
		    ciphertext="";
		}			
}