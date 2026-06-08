-- ================================================================
-- Seed data — roles and default admin user
-- ================================================================

USE access_control_db;

INSERT IGNORE INTO roles (role_name, description) VALUES
    ('admin',  'Full system access including user and privilege management'),
    ('editor', 'Can read and write data, cannot manage users'),
    ('viewer', 'Read-only access');

INSERT IGNORE INTO permissions (role_id, resource, can_read, can_write, can_delete) VALUES
    (1, 'users',      TRUE,  TRUE,  TRUE),
    (1, 'audit_log',  TRUE,  FALSE, FALSE),
    (1, 'privileges', TRUE,  TRUE,  TRUE),
    (2, 'data',       TRUE,  TRUE,  FALSE),
    (3, 'data',       TRUE,  FALSE, FALSE);
