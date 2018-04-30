<?php
require "connectdb.php";

if (!isset($_GET["obec"]) || !isset($_GET["momc"]) || !isset($_GET["okrsek"])) {
	echo "no-results";
	exit();
}

$stmt = $db->prepare('SELECT id, obec, momc, okrsek, pocet_volicu, ucast, other, ods,
					cssd, stan, kscm, zeleni, svobodni, pirati, top09, ano, kducsl, spd
					FROM public.snemovna2017 AS s WHERE s.obec=? AND s.momc=? AND s.okrsek=?;');
$stmt->bindParam(1, $_GET["obec"]);
$stmt->bindParam(2, $_GET["momc"]);
$stmt->bindParam(3, $_GET["okrsek"]);
$stmt->execute();
if ($stmt) {
	$row = $stmt->fetch(PDO::FETCH_ASSOC);
	if($row == false) {
		echo "no-results";
	} else {
		$row["type"] = "snemovna2017";
		echo json_encode($row);
	}
}
?>
