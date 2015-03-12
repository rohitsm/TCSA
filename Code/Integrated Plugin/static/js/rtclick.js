var item = "";
$(function(e){
    $.contextMenu({
        selector: '.haha', 
        callback: function(key, options) {
            var m = "clicked: " + key;
            if(key==="delete"){
        var username= "admin@tcsa.com";
              var filename= localStorage.getItem("path");
              filename+="/"+item;
              var todelete=filename;
              filename = password.substring(0,10) + filename;
              filename = Sha256.hash(filename);
              alert("deleting " + filename);
              deleteFile(username,filename,todelete);
              
            }
            //window.console && console.log(m) || alert(m); 
        },
        items: {
            "delete": {name: "Delete", icon: "delete"},
            "sep1": "---------",
            "newFolder": { name: "New Folder", icon: "Folder"},
            "quit": {name: "Quit", icon: "quit"}
        }
    });
    
    $('.haha').on('mousedown', function(e){
      if(e.which==3) {
        item = $(e.target).text();
        console.log('clicked', item);
      }
          
    })
});