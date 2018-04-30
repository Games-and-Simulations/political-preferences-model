<?php
require "connectdb.php";

if (!isset($_GET["obec"]) || !isset($_GET["momc"]) || !isset($_GET["okrsek"]) || !isset($_GET["modelid"])) {
	echo "no-results";
	exit();
}
if (!ctype_digit($_GET["modelid"])) {
	echo "no-results";
	exit();	
}
$tablename = "model" . $_GET["modelid"];

$stmt = $db->prepare('SELECT * FROM '. $tablename .' AS s WHERE s.obec=? AND s.momc=? AND s.okrsek=?;');
$stmt->bindParam(1, $_GET["obec"]);
$stmt->bindParam(2, $_GET["momc"]);
$stmt->bindParam(3, $_GET["okrsek"]);
$stmt->execute();
if ($stmt) {
	$row = $stmt->fetch(PDO::FETCH_ASSOC);
	if($row == false) {
		echo "no-results";
	} else {
		$row["type"] = $tablename;
		echo json_encode($row);
	}
}
?>
