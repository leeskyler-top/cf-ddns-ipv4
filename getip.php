<?php
$ip = $_SERVER['REMOTE_ADDR'];
header('Content-Type: application/json');
echo json_encode([
    "ip" => $ip
]);