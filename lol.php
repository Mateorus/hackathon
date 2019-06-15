<?php
$name = $_POST['username'];
$pas = $_POST['password'];
$filename = $_FILES['userfile']['name'];
echo "name = ".$name." password = ".$pas." ";
print_r($_FILES);
?>