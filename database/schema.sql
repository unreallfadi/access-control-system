-- ============================================================
-- User Authentication & Access Control System
-- Author: Fadi Amir
-- Description: Role-based access control with full audit logging
-- ============================================================

CREATE DATABASE IF NOT EXISTS access_control_db;
USE access_control_db;

-- ----------------------------------------------------------------
-- Roles table: defines permission levels
-- ----------------------------------------------------------------
CREATE TABLE roles (
    role_id   INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    can_read  BOOLEAN DEFAULT TRUE,
    can_write BOOLEAN DEFAULT FALSE,
    can_delete BOOLEAN DEFAULT FALSE,
    can_manage_users BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------
-- Users table: system accounts
-- ----------------------------------------------------------------
CREATE TABLE users (
    user_id       INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(100) NOT NULL UNIQUE,
    email         VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role_id       INT NOT NULL,
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login    DATETIME NULL,
    FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE RESTRICT
);

-- ----------------------------------------------------------------
-- Permissions table: documents what each role can access
-- ----------------------------------------------------------------
CREATE TABLE permissions (
    permission_id   INT AUTO_INCREMENT PRIMARY KEY,
    role_id         INT NOT NULL,
    resource_name   VARCHAR(100) NOT NULL,  -- e.g. 'users', 'reports', 'settings'
    action          ENUM('read', 'write', 'delete', 'manage') NOT NULL,
    granted         BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE,
    UNIQUE KEY unique_role_resource_action (role_id, resource_name, action)
);

-- ----------------------------------------------------------------
-- Audit log: every login attempt recorded here
-- ----------------------------------------------------------------
CREATE TABLE audit_log (
    log_id     INT AUTO_INCREMENT PRIMARY KEY,
    username   VARCHAR(100) NOT NULL,       -- store as-is, even if user deleted
    ip_address VARCHAR(45) NOT NULL,
    action     VARCHAR(100) NOT NULL,       -- e.g. 'LOGIN_SUCCESS', 'LOGIN_FAIL', 'USER_CREATED'
    status     ENUM('success', 'failed', 'warning') NOT NULL,
    details    TEXT NULL,
    logged_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_logged_at (logged_at),
    INDEX idx_status (status)
);
