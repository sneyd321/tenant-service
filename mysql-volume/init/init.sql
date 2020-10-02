
CREATE DATABASE IF NOT EXISTS roomr;
USE roomr;

CREATE USER 'admin'@'%' IDENTIFIED BY 'admin';
GRANT ALL PRIVILEGES ON roomr.* TO 'admin'@'%';


FLUSH privileges;