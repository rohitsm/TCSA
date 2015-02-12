

<?php 

if(isset($_FILES['file']) and !$_FILES['file']['error']){
    $fname = "test.txt";

    move_uploaded_file($_FILES['file']['tmp_name'], $fname);
}
?>