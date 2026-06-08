"""
Multi-User Database Access Control System
DBA-Grade Edition

Author: Fadi Amir
Stack:  Python Flask + MySQL
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from flask_mysqldb import MySQL
from functools import wraps
import bcrypt
import os
import csv
import io
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change_this_in_production')

# ----------------------------------------------------------------
# Database configuration
# ----------------------------------------------------------------
app.config['MYSQL_HOST']        = 'localhost'
app.config['MYSQL_USER']        = 'root'
app.config['MYSQL_PASSWORD']    = 'your_mysql_password'
app.config['MYSQL_DB']          = 'access_control_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# ----------------------------------------------------------------
# Password policy
# ----------------------------------------------------------------
PASSWORD_MIN_LENGTH  = 8
PASSWORD_REQUIRE_NUM = True
PASSWORD_REQUIRE_SYM = True

def validate_password(password: str):
    """Enforce password policy. Returns (is_valid, error_message)."""
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f'Password must be at least {PASSWORD_MIN_LENGTH} characters.'
    if PASSWORD_REQUIRE_NUM and not any(c.isdigit() for c in password):
        return False, 'Password must contain at least one number.'
    if PASSWORD_REQUIRE_SYM and not any(c in '!@#$%^&*()_+-=[]{}' for c in password):
        return False, 'Password must contain at least one special character.'
    return True, ''

# ----------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------
def log_action(username, action, status, details=None):
    """Write an entry to the audit log."""
    ip  = request.remote_addr or '0.0.0.0'
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO audit_log (username, ip_address, action, status, details) VALUES (%s, %s, %s, %s, %s)",
        (username, ip, action, status, details)
    )
    mysql.connection.commit()
    cur.close()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Access denied. Admin role required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

# ----------------------------------------------------------------
# Auth routes
# ----------------------------------------------------------------
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].encode('utf-8')

        cur = mysql.connection.cursor()
        cur.execute(
            """SELECT u.*, r.role_name
               FROM users u
               JOIN roles r ON u.role_id = r.role_id
               WHERE u.username = %s AND u.is_active = TRUE""",
            (username,)
        )
        user = cur.fetchone()

        if user and bcrypt.checkpw(password, user['password_hash'].encode('utf-8')):
            session['user_id']  = user['user_id']
            session['username'] = user['username']
            session['role']     = user['role_name']

            cur.execute("UPDATE users SET last_login = %s WHERE user_id = %s",
                        (datetime.now(), user['user_id']))
            mysql.connection.commit()
            cur.close()

            log_action(username, 'LOGIN_SUCCESS', 'success')
            return redirect(url_for('dashboard'))
        else:
            cur.close()
            log_action(username, 'LOGIN_FAIL', 'failed', 'Invalid credentials')
            flash('Invalid username or password.', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    log_action(session['username'], 'LOGOUT', 'success')
    session.clear()
    return redirect(url_for('login'))

# ----------------------------------------------------------------
# Dashboard
# ----------------------------------------------------------------
@app.route('/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) AS total FROM users WHERE is_active = TRUE")
    total_users = cur.fetchone()['total']

    cur.execute("""SELECT COUNT(*) AS total FROM audit_log
                   WHERE status = 'failed' AND DATE(logged_at) = CURDATE()""")
    failed_today = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) AS total FROM roles")
    total_roles = cur.fetchone()['total']

    # DB health: table sizes
    cur.execute("""
        SELECT table_name,
               IFNULL(table_rows, 0) AS table_rows,
               ROUND((data_length + index_length) / 1024, 2) AS size_kb
        FROM information_schema.tables
        WHERE table_schema = %s
        ORDER BY size_kb DESC
    """, (app.config['MYSQL_DB'],))
    table_stats = cur.fetchall()

    cur.execute("SELECT * FROM audit_log ORDER BY logged_at DESC LIMIT 10")
    recent_logs = cur.fetchall()

    cur.close()

    return render_template('dashboard.html',
                           total_users=total_users,
                           failed_today=failed_today,
                           total_roles=total_roles,
                           table_stats=table_stats,
                           recent_logs=recent_logs)

# ----------------------------------------------------------------
# User management
# ----------------------------------------------------------------
@app.route('/users')
@login_required
@admin_required
def users():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT u.user_id, u.username, u.email, u.is_active,
               u.created_at, u.last_login, r.role_name
        FROM users u
        JOIN roles r ON u.role_id = r.role_id
        ORDER BY u.created_at DESC
    """)
    all_users = cur.fetchall()

    cur.execute("SELECT * FROM roles ORDER BY role_name")
    all_roles = cur.fetchall()
    cur.close()

    return render_template('users.html', users=all_users, roles=all_roles)


@app.route('/users/create', methods=['POST'])
@login_required
@admin_required
def create_user():
    username = request.form['username'].strip()
    email    = request.form['email'].strip()
    password = request.form['password']
    role_id  = request.form['role_id']

    valid, msg = validate_password(password)
    if not valid:
        flash(msg, 'error')
        return redirect(url_for('users'))

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    cur = mysql.connection.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, email, password_hash, role_id) VALUES (%s, %s, %s, %s)",
            (username, email, password_hash, role_id)
        )
        mysql.connection.commit()
        log_action(session['username'], 'USER_CREATED', 'success', f'Created user: {username}')
        flash(f'User {username} created successfully.', 'success')
    except Exception as e:
        mysql.connection.rollback()
        log_action(session['username'], 'USER_CREATE_FAIL', 'failed', str(e))
        flash('Failed to create user. Username or email may already exist.', 'error')
    finally:
        cur.close()

    return redirect(url_for('users'))


@app.route('/users/toggle/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT username, is_active FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()

    if user:
        new_status = not user['is_active']
        cur.execute("UPDATE users SET is_active = %s WHERE user_id = %s", (new_status, user_id))
        mysql.connection.commit()
        action = 'USER_ENABLED' if new_status else 'USER_DISABLED'
        log_action(session['username'], action, 'success', f'Target: {user["username"]}')
        flash(f'User {user["username"]} {"enabled" if new_status else "disabled"}.', 'success')

    cur.close()
    return redirect(url_for('users'))


@app.route('/users/reset-password/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def reset_password(user_id):
    new_password = request.form['new_password']

    valid, msg = validate_password(new_password)
    if not valid:
        flash(msg, 'error')
        return redirect(url_for('users'))

    password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    cur = mysql.connection.cursor()
    cur.execute("SELECT username FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()

    if user:
        cur.execute("UPDATE users SET password_hash = %s WHERE user_id = %s",
                    (password_hash, user_id))
        mysql.connection.commit()
        log_action(session['username'], 'PASSWORD_RESET', 'success',
                   f'Reset password for: {user["username"]}')
        flash(f'Password reset for {user["username"]}.', 'success')

    cur.close()
    return redirect(url_for('users'))

# ----------------------------------------------------------------
# DB Privilege management (DBA feature)
# ----------------------------------------------------------------
@app.route('/privileges')
@login_required
@admin_required
def privileges():
    cur = mysql.connection.cursor()

    cur.execute("SELECT user, host FROM mysql.user ORDER BY user")
    db_users = cur.fetchall()

    cur.execute("""
        SELECT schema_name FROM information_schema.schemata
        WHERE schema_name NOT IN
              ('information_schema','mysql','performance_schema','sys')
        ORDER BY schema_name
    """)
    databases = cur.fetchall()

    cur.close()
    return render_template('privileges.html', db_users=db_users, databases=databases)


@app.route('/privileges/grant', methods=['POST'])
@login_required
@admin_required
def grant_privilege():
    db_user   = request.form['db_user']
    db_host   = request.form['db_host']
    privilege = request.form['privilege'].upper()
    database  = request.form['database']
    table     = request.form.get('table', '*') or '*'

    allowed = {'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'ALL PRIVILEGES'}
    if privilege not in allowed:
        flash('Invalid privilege type.', 'error')
        return redirect(url_for('privileges'))

    cur = mysql.connection.cursor()
    try:
        cur.execute(
            f"GRANT {privilege} ON `{database}`.`{table}` TO %s@%s",
            (db_user, db_host)
        )
        cur.execute("FLUSH PRIVILEGES")
        mysql.connection.commit()
        log_action(session['username'], 'PRIVILEGE_GRANTED', 'success',
                   f'GRANT {privilege} ON {database}.{table} TO {db_user}@{db_host}')
        flash(f'Granted {privilege} on {database}.{table} to {db_user}@{db_host}.', 'success')
    except Exception as e:
        log_action(session['username'], 'PRIVILEGE_GRANT_FAIL', 'failed', str(e))
        flash(f'Failed to grant privilege: {e}', 'error')
    finally:
        cur.close()

    return redirect(url_for('privileges'))


@app.route('/privileges/revoke', methods=['POST'])
@login_required
@admin_required
def revoke_privilege():
    db_user   = request.form['db_user']
    db_host   = request.form['db_host']
    privilege = request.form['privilege'].upper()
    database  = request.form['database']
    table     = request.form.get('table', '*') or '*'

    allowed = {'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'ALL PRIVILEGES'}
    if privilege not in allowed:
        flash('Invalid privilege type.', 'error')
        return redirect(url_for('privileges'))

    cur = mysql.connection.cursor()
    try:
        cur.execute(
            f"REVOKE {privilege} ON `{database}`.`{table}` FROM %s@%s",
            (db_user, db_host)
        )
        cur.execute("FLUSH PRIVILEGES")
        mysql.connection.commit()
        log_action(session['username'], 'PRIVILEGE_REVOKED', 'success',
                   f'REVOKE {privilege} ON {database}.{table} FROM {db_user}@{db_host}')
        flash(f'Revoked {privilege} on {database}.{table} from {db_user}@{db_host}.', 'success')
    except Exception as e:
        log_action(session['username'], 'PRIVILEGE_REVOKE_FAIL', 'failed', str(e))
        flash(f'Failed to revoke privilege: {e}', 'error')
    finally:
        cur.close()

    return redirect(url_for('privileges'))

# ----------------------------------------------------------------
# Permissions report
# ----------------------------------------------------------------
@app.route('/report')
@login_required
@admin_required
def permissions_report():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT grantee, table_catalog, table_schema, privilege_type, is_grantable
        FROM information_schema.schema_privileges
        ORDER BY grantee, table_schema
    """)
    schema_privs = cur.fetchall()

    cur.execute("""
        SELECT grantee, table_schema, table_name, privilege_type, is_grantable
        FROM information_schema.table_privileges
        ORDER BY grantee, table_schema, table_name
    """)
    table_privs = cur.fetchall()
    cur.close()

    return render_template('report.html',
                           schema_privs=schema_privs,
                           table_privs=table_privs,
                           generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


@app.route('/report/export')
@login_required
@admin_required
def export_report():
    """Export permissions report as CSV."""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT grantee, table_schema AS database_name, table_name,
               privilege_type, is_grantable
        FROM information_schema.table_privileges
        ORDER BY grantee, table_schema, table_name
    """)
    rows = cur.fetchall()
    cur.close()

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['grantee', 'database_name',
                                                 'table_name', 'privilege_type',
                                                 'is_grantable'])
    writer.writeheader()
    writer.writerows(rows)

    log_action(session['username'], 'REPORT_EXPORTED', 'success', 'Permissions CSV export')

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=permissions_report.csv'}
    )

# ----------------------------------------------------------------
# Audit log
# ----------------------------------------------------------------
@app.route('/audit')
@login_required
@admin_required
def audit():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM audit_log ORDER BY logged_at DESC LIMIT 200")
    logs = cur.fetchall()
    cur.close()
    return render_template('audit.html', logs=logs)


if __name__ == '__main__':
    app.run(debug=False)
