-- =========================================================
-- AI-POWERED CUSTOMER SUPPORT & HELPDESK PLATFORM
-- MYSQL RELATIONAL DATABASE ARCHITECTURE DDL
-- Generated automatically from SQLAlchemy ORM Metadata
-- Target Database: customer_support_db (utf8mb4 / InnoDB)
-- =========================================================

CREATE DATABASE IF NOT EXISTS customer_support_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE customer_support_db;

SET FOREIGN_KEY_CHECKS = 0;

-- Table structure for `app_settings`
DROP TABLE IF EXISTS `app_settings`;
CREATE TABLE app_settings (
	`key` VARCHAR(80) NOT NULL, 
	value VARCHAR(255) NOT NULL, 
	PRIMARY KEY (`key`)
);

-- Table structure for `knowledge_categories`
DROP TABLE IF EXISTS `knowledge_categories`;
CREATE TABLE knowledge_categories (
	category_id INTEGER NOT NULL AUTO_INCREMENT, 
	category_name VARCHAR(100) NOT NULL, 
	description VARCHAR(255), 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (category_id), 
	UNIQUE (category_name)
);

-- Table structure for `ticket_categories`
DROP TABLE IF EXISTS `ticket_categories`;
CREATE TABLE ticket_categories (
	category_id INTEGER NOT NULL AUTO_INCREMENT, 
	category_name VARCHAR(100) NOT NULL, 
	description VARCHAR(255), 
	is_active BOOL NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (category_id), 
	UNIQUE (category_name)
);

-- Table structure for `token_blocklist`
DROP TABLE IF EXISTS `token_blocklist`;
CREATE TABLE token_blocklist (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	jti VARCHAR(64) NOT NULL, 
	expires_at DATETIME NOT NULL, 
	PRIMARY KEY (id)
);

-- Table structure for `users`
DROP TABLE IF EXISTS `users`;
CREATE TABLE users (
	user_id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(120) NOT NULL, 
	email VARCHAR(190) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	`role` ENUM('admin','agent','customer') NOT NULL, 
	account_status ENUM('active','inactive') NOT NULL, 
	is_seed BOOL NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (user_id)
);

-- Table structure for `audit_logs`
DROP TABLE IF EXISTS `audit_logs`;
CREATE TABLE audit_logs (
	log_id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER, 
	action VARCHAR(60) NOT NULL, 
	entity_type VARCHAR(40) NOT NULL, 
	entity_id INTEGER, 
	description VARCHAR(500), 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (log_id), 
	FOREIGN KEY(user_id) REFERENCES users (user_id)
);

-- Table structure for `knowledge_articles`
DROP TABLE IF EXISTS `knowledge_articles`;
CREATE TABLE knowledge_articles (
	article_id INTEGER NOT NULL AUTO_INCREMENT, 
	category_id INTEGER NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	content TEXT NOT NULL, 
	status ENUM('draft','published','archived') NOT NULL, 
	created_by INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (article_id), 
	FOREIGN KEY(category_id) REFERENCES knowledge_categories (category_id), 
	FOREIGN KEY(created_by) REFERENCES users (user_id)
);

-- Table structure for `saved_replies`
DROP TABLE IF EXISTS `saved_replies`;
CREATE TABLE saved_replies (
	reply_id INTEGER NOT NULL AUTO_INCREMENT, 
	created_by INTEGER NOT NULL, 
	title VARCHAR(120) NOT NULL, 
	reply_content TEXT NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (reply_id), 
	FOREIGN KEY(created_by) REFERENCES users (user_id)
);

-- Table structure for `tickets`
DROP TABLE IF EXISTS `tickets`;
CREATE TABLE tickets (
	ticket_id INTEGER NOT NULL AUTO_INCREMENT, 
	ticket_number VARCHAR(30) NOT NULL, 
	customer_id INTEGER NOT NULL, 
	assigned_agent_id INTEGER, 
	category_id INTEGER NOT NULL, 
	subject VARCHAR(200) NOT NULL, 
	description TEXT NOT NULL, 
	priority ENUM('low','medium','high','critical') NOT NULL, 
	status ENUM('open','assigned','in_progress','waiting_for_customer','resolved','closed') NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	resolved_at DATETIME, 
	closed_at DATETIME, 
	PRIMARY KEY (ticket_id), 
	UNIQUE (ticket_number), 
	FOREIGN KEY(customer_id) REFERENCES users (user_id), 
	FOREIGN KEY(assigned_agent_id) REFERENCES users (user_id), 
	FOREIGN KEY(category_id) REFERENCES ticket_categories (category_id)
);

-- Table structure for `notifications`
DROP TABLE IF EXISTS `notifications`;
CREATE TABLE notifications (
	notification_id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER NOT NULL, 
	title VARCHAR(150) NOT NULL, 
	message VARCHAR(500) NOT NULL, 
	notification_type VARCHAR(40) NOT NULL, 
	related_ticket_id INTEGER, 
	is_read BOOL NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (notification_id), 
	FOREIGN KEY(user_id) REFERENCES users (user_id), 
	FOREIGN KEY(related_ticket_id) REFERENCES tickets (ticket_id)
);

-- Table structure for `sla_records`
DROP TABLE IF EXISTS `sla_records`;
CREATE TABLE sla_records (
	sla_id INTEGER NOT NULL AUTO_INCREMENT, 
	ticket_id INTEGER NOT NULL, 
	response_due_at DATETIME NOT NULL, 
	resolution_due_at DATETIME NOT NULL, 
	first_response_at DATETIME, 
	resolved_at DATETIME, 
	sla_status ENUM('on_track','at_risk','breached','met') NOT NULL, 
	PRIMARY KEY (sla_id), 
	UNIQUE (ticket_id), 
	FOREIGN KEY(ticket_id) REFERENCES tickets (ticket_id)
);

-- Table structure for `ticket_messages`
DROP TABLE IF EXISTS `ticket_messages`;
CREATE TABLE ticket_messages (
	message_id INTEGER NOT NULL AUTO_INCREMENT, 
	ticket_id INTEGER NOT NULL, 
	sender_id INTEGER NOT NULL, 
	message_content TEXT NOT NULL, 
	message_type ENUM('public','internal') NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (message_id), 
	FOREIGN KEY(ticket_id) REFERENCES tickets (ticket_id), 
	FOREIGN KEY(sender_id) REFERENCES users (user_id)
);

-- Table structure for `ticket_status_history`
DROP TABLE IF EXISTS `ticket_status_history`;
CREATE TABLE ticket_status_history (
	history_id INTEGER NOT NULL AUTO_INCREMENT, 
	ticket_id INTEGER NOT NULL, 
	changed_by INTEGER NOT NULL, 
	event_type VARCHAR(20) NOT NULL, 
	old_status VARCHAR(60), 
	new_status VARCHAR(60), 
	remarks VARCHAR(500), 
	changed_at DATETIME NOT NULL, 
	PRIMARY KEY (history_id), 
	FOREIGN KEY(ticket_id) REFERENCES tickets (ticket_id), 
	FOREIGN KEY(changed_by) REFERENCES users (user_id)
);

-- Table structure for `ticket_attachments`
DROP TABLE IF EXISTS `ticket_attachments`;
CREATE TABLE ticket_attachments (
	attachment_id INTEGER NOT NULL AUTO_INCREMENT, 
	ticket_id INTEGER NOT NULL, 
	message_id INTEGER, 
	uploaded_by INTEGER NOT NULL, 
	original_filename VARCHAR(255) NOT NULL, 
	stored_filename VARCHAR(255) NOT NULL, 
	file_path VARCHAR(500) NOT NULL, 
	mime_type VARCHAR(100) NOT NULL, 
	file_size INTEGER NOT NULL, 
	uploaded_at DATETIME NOT NULL, 
	is_internal BOOL NOT NULL, 
	PRIMARY KEY (attachment_id), 
	FOREIGN KEY(ticket_id) REFERENCES tickets (ticket_id), 
	FOREIGN KEY(message_id) REFERENCES ticket_messages (message_id), 
	FOREIGN KEY(uploaded_by) REFERENCES users (user_id), 
	UNIQUE (stored_filename)
);

SET FOREIGN_KEY_CHECKS = 1;
