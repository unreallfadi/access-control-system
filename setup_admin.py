"""
Run this once after setting up the database to create the admin account.
Usage: python setup_admin.py
"""

import bcrypt
import MySQLdb

# Update these values
DB_HOST     = 'localhost'
DB_USER     = 'root'
DB_PASSWORD = 'your_mysql_password'
DB_NAME     = 'access_control_db'

ADMIN_USERNAME = 'admin'
ADMIN_EMAIL    = 'admin@system.local'
ADMIN_PASSWORD = 'Admin@1234'  # Change this after first login

def main():
    password_hash = bcrypt.hashpw(ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conn = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)
    cur  = conn.cursor()

    cur.execute(
        "UPDATE users SET password_hash = %s WHERE username = %s",
        (password_hash, ADMIN_USERNAME)
    )
    conn.commit()
    cur.close()
    conn.close()

    print(f"Admin password set successfully.")
    print(f"Username: {ADMIN_USERNAME}")
    print(f"Password: {ADMIN_PASSWORD}")
    print("Change your password after first login.")

if __name__ == '__main__':
    main()
