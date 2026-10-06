CREATE DATABASE IF NOT EXISTS lds_practice
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

GRANT SELECT, INSERT ON lds_practice.* TO 'rosuser'@'localhost';

USE lds_practice;

CREATE TABLE IF NOT EXISTS lidardata (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `ranges` JSON NOT NULL,
    `when` DATETIME(6) NOT NULL COMMENT 'UTC measurement time',
    `action` VARCHAR(16) NOT NULL,
    INDEX idx_when (`when`)
);
