-- ============================================================
-- Seed Data: default roles and admin account
-- ============================================================
USE access_control_db;

-- Default roles
INSERT INTO roles (role_name, can_read, can_write, can_delete, can_manage_users) VALUES
('admin',  TRUE, TRUE,  TRUE,  TRUE),
('editor', TRUE, TRUE,  FALSE, FALSE),
('viewer', TRUE, FALSE, FALSE, FALSE);

-- Default permissions per role
-- Admin
INSERT INTO permissions (role_id, resource_name, action, granted) VALUES
(1, 'users',    'read',   TRUE),
(1, 'users',    'write',  TRUE),
(1, 'users',    'delete', TRUE),
(1, 'users',    'manage', TRUE),
(1, 'reports',  'read',   TRUE),
(1, 'reports',  'write',  TRUE),
(1, 'settings', 'manage', TRUE);

-- Editor
INSERT INTO permissions (role_id, resource_name, action, granted) VALUES
(2, 'users',   'read',  TRUE),
(2, 'reports', 'read',  TRUE),
(2, 'reports', 'write', TRUE);

-- Viewer
INSERT INTO permissions (role_id, resource_name, action, granted) VALUES
(3, 'users',   'read', TRUE),
(3, 'reports', 'read', TRUE);

-- Default admin account
-- Password: Admin@1234 (bcrypt hashed - replace after first login)
INSERT INTO users (username, email, password_hash, role_id) VALUES
('admin', 'admin@system.local', '$2b$12$placeholder_replace_on_first_run', 1);
