encryptedMetadata="AwLGq7W/9lSIDn7w5QDerVGZq+2NJjubQXNEaHE8H75XJYPzfyYm02xUa0pws8NEAIQBxGuBGg2/VjC9p0ZcoZm2mhaWgoKgJBLKJ5ga8sn/HU8pOc6rDmzGT8GCcfxGBai+B6DyvDH2QXIz2INsSpO87cxjV/asTvzgtviIlOODFY1TKO7o/6mM8dgBZnNdq+lkCt/jtdNVhGCjwtJma4lLghuoEnLa4lwPm7oyunMQZQ35SnE3FF33Ym+wOfmzgQdqyZSXS4aivM4d8byaxobJn0JpeU6HEe50Kj84iXOfprTuZTNLypSGbpnuAkz8LPrHTlnEssBnCxTqjkZBJRUsGTtBT+uQ3XNo0YHRp5kef/NUS7mC5Xgy6PJjqayb9srfcTQp0JFHZv1iAxekDDREhP53jIv8wYprwFXuPYsa1MB+C8odlk96UOjPQ8QXBU1ou0O2c2siwNKjXRUkKtBF8ppJepF+fup6HCKebYYMRCCzbUTBTRm7q/9w2ALPDKRlyVmH3MrE0IjDy6i+rI6ZJF9O2qC2AKu3vb1IvXbaTtHVvaqA/wAtEGMTTq5luHmcMEIzEXfFKBZtwKqg2GnmXZDYVSebGcpra0zlNBCKpy2UmcCoFHpuEYv0jHRoLymz+Skqp0ET+BULnuMSJDNUT7LzutGs2jWT0LvhfnUs2T8nY4rJavtIoHBgTAwbZe+zTVohWRrj69K2dLn+XU3/ZUwmVv0EYanUXBch+ZmMzOYkFaRzXa/SL2wJkJXOQnlPdF7bTv6C/WOGhEP/B6zqSUTUKPUbl7wYqLEx7/+EWR7oSNZ5KrS9iZn2gsG5pXREvytft1k4cAj/mVLNghy0VkG04vnsui+I2vPm0/yXY9TCUCwJ2gWuaFAY3uLGYpK1IudYm01db+RHgAJU1ITFCZBZQnN3svAlSfkgI86SeUehiTVJrEchWrBuC9GgX7FNbwvMaBa83KF1nQMgogWqSVXEfZxlOfs7usL8MJ1cXAJjOhDQX+5/jy1AB0YxhAxaq+zF/4tFW/rjOv/26VLHABLVyJXE5I9wTsyX4YJneV3zPKg66d1LV5+YNhFch0eW4zixYwSroi3YIvbuv35wV5vX1Vjm8vMDJblEqu+M7qLf2cf8xD9kGMBu/rtKBufJ/hlGBwAi94O7vpP+VzotS5loUvZ3E4ltjHbrmjFuHqXOgrop//PBdItZXJq7z+QeRL0kOY70/KQI2pqChl7woOSOcrB9mtOHqwijORbNNCpZFdHp2ec+tFVivllrP18zrsl8QkbU5ah3PM1JbB20V4x0o545h/p9My0m2s2pxm5xyjDRsmshzye/HIZaR7CgB0LMWCaI8q9cCEkbFpgqpIXNEstnN1g8FKkGEsLIWS0FjP90Ll+/HVriUibJbtQw0B/cDxjRhkNAeZZFAlhsculzaJ+yYyYEQDIqGqEPTuQm4uZfx72IEqqQ3yQUvYpBECbkG8o9dVC/Y4YaELWEdPUywWnMGPsU0AiaalrJfrrEZvHLtoF64ni4dpx2/aeUfs52oNa12P+wced+e9mSlhLR1sKtqFLewrRJtoLK0SyJ3pLou/wdM8qAbhWCGL3FWDiaczQnUjEbcSEOu/YZcziLtvf66c4OALoUS2SjoWDg1VN6+Qxz3k5pJIb/hLRK59euFy4Msn7h2jjxdc1W1tJbu2l4x9YIVpzm2C6k8Ozrg6EB/6iBKmVuY9qXwd9zkTIfHANFAbVlk7d0C6cezkr+Xj5rxEDCLN2eqQTAu7VP7Ot1xwhg+57Cz1P7zGjzO8ImSaI=-";
var blobs = [];
var count=count2=0;
var plaintext="";
var password="appa1234";
var str=encryptedMetadata; //load file bytes to buffer
decryptMeta(str);
function decryptMeta(str){
	count=count2=0;
	var buf=str.split("-");
	for (var i = 0; i < buf.length-1; i++){
		blobs.push(new Blob([buf[i]]));
		count++;
	}
	decryptMetadata(blobs);
}


function decryptMetadata(e){

	  if(count2<count){
			var reader = new FileReader();
    		reader.readAsText(blobs[count2]);
    		reader.onload = function(evt) {
    			var content = reader.result;
		        plaintext += Aes.Ctr.decrypt(content, password, 256);
			}
			reader.onloadend= function(evt){
				count2=count2+1;
				decryptMetadata(evt);
			}
		}
		else{
			alert(plaintext);
			//plaintext+= "\n"+ "root/testing6/haha.jpg";
			localStorage.setItem("metadata",plaintext);
		}
}

$("#clear").click(function(){
	localStorage.removeItem("path");
});
				