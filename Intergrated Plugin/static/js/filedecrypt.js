var blobs = [];
var count=count2=0;
var plaintext="";
var contentBytes=[];
var password="appa1234";//localStorage.getItem("password");
var file;
var newstr='';
function decryptFileProcess(file){
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
				var filename = file.name.replace(/\.txt$/,'');
			    filename= Aes.Ctr.decrypt(filename, password, 256);
			    alert(filename);
			    //filename = filename.replace(/\.encrypted$/,'');
			    var removName= filename.substring(0,10);
			   	filename= filename.replace(removName, '');
			    saveAs(blob, filename);
			    plaintext="";
			    alert(filename);
				//alert(filename.toString(CryptoJS.enc.Utf8));
		}
				
}



