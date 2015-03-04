var tree = new TreeModel();
var root = tree.parse({id: '/'});
var currentPath = localStorage.getItem('path');	// take from local storage
if (currentPath == null) {
	currentPath="root";
	localStorage.setItem("path","root");
}


//var metadata = "root/testing1/pictures/dog/dog1.jpg\nroot/testing1/pictures/dog/dog2.jpg\nroot/testing1/pictures/cat/cat1.jpg\nroot/testing1/pictures/cat/dog2.jpg\nroot/testing1/movies/movie1/movie.mkv\nroot/testing1/movies/movie1/movie.srt\nroot/testing2/videos/video1.mp4\nroot/testing2/videos/video2.mp4\nroot/testing2/videos/schoolvideos/video1.mp4\nroot/testing2/videos/schoolvideos/video2.mp4\nroot/testing3/documents/school/module1/text1.doc\nroot/testing3/documents/school/module1/text2.doc\nroot/testing3/documents/school/module2/text1.doc\nroot/testing3/documents/school/module2/text2.doc\nroot/testing3/documents/school/module3/text1.doc\nroot/testing3/documents/school/module3/text2.doc\nroot/testing3/documents/school/module3/text3.doc\nroot/testing3/documents/school/module3/text4.doc\nroot/testing3/documents/work/file1.jpg\nroot/testing3/documents/work/file2.txt\nroot/testing3/documents/work/file3.mp4\nroot/testing4/dropbox/movie1.mp4\nroot/testing4/dropbox/text.doc\nroot/testing4/dropbox/song1.mp3\nroot/testing4/dropbox/program1.java\nroot/testing5/sound/TaylorSwift/song1.mp3\nroot/testing5/sound/TaylorSwift/song2.mp3\nroot/testing5/sound/TaylorSwift/song3.mp3\nroot/testing5/sound/TaylorSwift/song4.mp3\nroot/testing5/sound/TaylorSwift/song5.mp3\nroot/testing5/sound/song1.mp3\nroot/testing5/sound/song2.mp3\nroot/testing5/sound/song3.mp3\n";
var metadata=localStorage.getItem("metadata");
var html = "";
constructTree(metadata);
var children = getChildNodes(currentPath);

for(var i=0; i<children.length; i++) {
	if(children[i].lastIndexOf(".")==-1)
		html += '<img src = "img/folder.png">';
	else {
		var extension = children[i].split(".").pop();
		//extension = "file";
		html +=  '<object data="img/' + extension +'.png" type="image/png"> <img src="img/file.png" /> </object>';
	}

	html += '<a href= "index.html" class="haha">' + children[i] + '</a>' + '</br>';
}
document.getElementById("status").innerHTML = html;


$(".haha").click(function () {
 	var value = $(this).text();
 	var tempPath= localStorage.getItem('path');
 	tempPath+="/"+value;
 	 alert(tempPath);   
 	localStorage.setItem('path', tempPath);   
}); 


function traverse(path, curNode){
	var index = path.indexOf("/");
	if(index==0) {
		return root;
	}

	if(index == -1) {
		var tmpNode = curNode.first(function (node) {
    		return node.model.id === path;
		});
		return tmpNode;
	}
	
	var current = path.substring(0,index);
	var child = path.substring(index+1);

	var childNode = curNode.first(function (node) {
    	return node.model.id === current;
	});

	return traverse(child,childNode);
}

function getChildNodes(currentPath){

	var currentNode = traverse(currentPath,root);
	var childNodes = currentNode.children;
	var children = [];
	
	for (var i=0; i<childNodes.length; i++){
		children.push(childNodes[i].model.id);
	}

	return children;
}

function constructTree(metadata){
	var lines = metadata.split("\n");
	for(var i=0; i<lines.length; i++){
		var nodes = lines[i].split("/");
		var currentNode = root;
		//alert("current node is " + currentNode.model.id);
		for(var j=0; j<nodes.length; j++){
			// get node if it already exists
			var childNode = currentNode.first(function(node){
				return node.model.id === nodes[j];
			});
			// create node if it does not exist
			if (typeof childNode == 'undefined') {
				childNode = tree.parse({id: nodes[j]});
				currentNode.addChild(childNode);
			}
				//alert("child node is " + childNode.model.id);
			currentNode = childNode;
		}
	}
}

$("#home").click(function(){
	localStorage.removeItem("path");
	window.location="index.html";
});

$("#back").click(function(){
	var curPath=localStorage.getItem("path");
	var nodes=curPath.split("/");
	var newPath="root";
	for(var j=1; j<nodes.length-1; j++){
		newPath+="/"+nodes[j];
	}
	localStorage.setItem("path",newPath);
	window.location="index.html";
});