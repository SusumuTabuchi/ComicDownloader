<?php
/* ssl */
$cfg['Servers'][$i]['ssl'] = true;
// Client secret key
$cfg['Servers'][$i]['ssl_key'] = '/etc/ssl/certs/private/server.key';
// Client certificate
$cfg['Servers'][$i]['ssl_cert'] = '/etc/ssl/certs/server.csr';
// Server certification authority
// $cfg['Servers'][$i]['ssl_ca'] = '../server-ca.pem';
// // Disable SSL verification (see above note)
// $cfg['Servers'][$i]['ssl_verify'] = false;