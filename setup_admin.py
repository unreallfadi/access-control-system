"""
One-time script to create the default admin user.
Run once after setting up the database.

Usage: python setup_admin.py
"""

import bcrypt
import pymysql
import getpass

DB_CONFIG = {
    'host':   'localhost',
    'user':   'root',
    'passwd': input('MySQL root password: '),
    'db':     'access_control_db',
    'cursorclass': pymysql.cursors.DictCursor
}

password     = getpass.getpass('Set admin password: ')
confirm      = getpass.getpass('Confirm password: ')

if password != confirm:
    print('Passwords do not match.')
    exit(1)

if len(password) < 8:
    print('Password must be at least 8 characters.')
    exit(1)

password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

conn   = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

cursor.execute("SELECT role_id FROM roles WHERE role_name = 'admin'")
role = cursor.fetchone()

if not role:
    print('Admin role not found. Run schema.sql and seed.sql first.')
    exit(1)

cursor.execute("""
    INSERT INTO users (username, email, password_hash, role_id)
    VALUES ('admin', 'admin@system.local', %s, %s)
    ON DUPLICATE KEY UPDATE password_hash = %s
""", (password_hash, role['role_id'], password_hash))

conn.commit()
cursor.close()
conn.close()

print('Admin user created. Login at http://localhost:5000')
