function deleteFile(useremail,filename,todelete){
	//alert("user_email "+useremail+"\nfilename "+filename);
	//alert("Downloading "+ filename + " from user "+ useremail);
      data= { 
      		'req': 'delete',
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
          alert(status);
          if(status=='OK'){
          	alert("OK" + todelete);
            var metadata= localStorage.getItem("metadata");
            test=metadata.replace("\n"+todelete,"");
            localStorage.setItem("metadata",test);
            window.location="index.html";
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