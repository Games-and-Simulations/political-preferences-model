<?php
require "connectdb.php";

$json = json_decode(file_get_contents('php://input'));

$idArray = $json->idArray;

$jsonArray = array();

foreach ($idArray as $id) {
	$stmt = $db->prepare('SELECT id, obec, momc, okrsek, pocet_volicu, ucast, other, ods,
					cssd, stan, kscm, zeleni, svobodni, pirati, top09, ano, kducsl, spd
					FROM public.snemovna2017 AS s WHERE s.obec=? AND s.momc=? AND s.okrsek=?;');
	$stmt->bindParam(1, $id[0]);
	$stmt->bindParam(2, $id[1]);
	$stmt->bindParam(3, $id[2]);
	$stmt->execute();
	
	if ($stmt) {
		$row = $stmt->fetch(PDO::FETCH_ASSOC);
		if($row == false) {
			echo "no-results";
		} else {
			$row["type"] = "snemovna2017";
			array_push($jsonArray, json_encode($row));
		}
	}
}	
$jsonObject["resultArray"] = $jsonArray;
echo json_encode($jsonObject);
?>
