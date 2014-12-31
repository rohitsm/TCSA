var blobs = [];
var count=count2=0;
var plaintext="";
var contentBytes=[];
var password="appa";
var file;
var newstr='';
function decryptFileProcess(file){
	alert("filesplit decrypt");
	var fr = new FileReader();
	fr.readAsText(file);
	
	fr.onload = function(e) {
	  var str=e.target.result; //load file bytes to buffer
	  var buf=str.split("-");
	  
		for (var i = 0; i < buf.length-1; i++){
	    	blobs.push(new Blob([buf[i]]));
	    	count++;
	    }
	};
}

function decryptFile(e){
		alert("count "+ count + "count2 "+ count2);
		if(count2<count){
			var reader = new FileReader();
    		reader.readAsText(blobs[count2]);
    		reader.onload = function(evt) {
    			var content = reader.result;
		        plaintext += Aes.Ctr.decrypt(content, password, 256);
				count2=count2+1;
				
			}
		}
		else{

				contentBytes = new Uint8Array(plaintext.length);
		        for (var i=0; i<plaintext.length; i++) {
		            contentBytes[i] = plaintext.charCodeAt(i);
		        }

				var blob = new Blob([contentBytes], { type: 'application/octet-stream' });
			    alert(blob.size);
			    var filename = file.name.replace(/\.encrypted$/,'')+count2;
			    saveAs(blob, filename);
				alert(filename);
		}
				
}
