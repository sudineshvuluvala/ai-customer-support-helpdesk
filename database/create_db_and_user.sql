-- =========================================================
-- CREATE DATABASE AND LEAST-PRIVILEGE USER FOR HELPDESK
-- Run this as MySQL root user or an RDS master administrator
-- =========================================================

-- 1. Create dedicated database
CREATE DATABASE IF NOT EXISTS customer_support_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- 2. Create least-privilege application user
-- CHANGE 'replace_with_secure_password_123' to a strong secret
CREATE USER IF NOT EXISTS 'helpdesk_user'@'%' IDENTIFIED BY 'replace_with_secure_password_123';

-- 3. Grant required operational privileges
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, INDEX, REFERENCES
  ON customer_support_db.*
  TO 'helpdesk_user'@'%';

-- 4. Apply changes
FLUSH PRIVILEGES;
