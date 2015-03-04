var tree = new TreeModel();
var root = tree.parse({id: '/'});
var currentPath = "a/bb";	// take from local storage


var metadata = "a/bb/cc.zip\na/bb/ccc";
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
    alert(value);     
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
	//	alert("current node is " + currentNode.model.id);
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
			//	alert("child node is " + childNode.model.id);
			currentNode = childNode;
		}
	}
}