$(document).ready(function(){
	//root/aaa/bbbb/ccc.jpg
	//root/aaa/dd.txt
	//root/aaa/ee/ccc.jpg
	var folderTree=document.getElementById("folderTree");
	$("#newFolder").click(function(){
		var foldername = prompt("Please enter the folder name");
		if(foldername==""){
			foldername="New Folder";
		}
		folderTree.innerHTML= "<a href=\"filedisplay.html\" id=\""+ foldername.replace(/\s+/g,'') + "\">"+foldername+"</a>";
		
		
	});
});