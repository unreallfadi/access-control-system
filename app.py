"""
User Authentication & Access Control System
Author: Fadi Amir
Stack: Python Flask + MySQL
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from functools import wraps
import bcrypt
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change_this_in_production')

# ----------------------------------------------------------------
# Database configuration - update with your MySQL credentials
# ----------------------------------------------------------------
app.config['MYSQL_HOST']     = 'localhost'
app.config['MYSQL_USER']     = 'root'
app.config['MYSQL_PASSWORD'] = 'your_mysql_password'
app.config['MYSQL_DB']       = 'access_control_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


# ----------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------

def log_action(username, action, status, details=None):
    """Write an entry to the audit log."""
    ip = request.remote_addr or '0.0.0.0'
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO audit_log (username, ip_address, action, status, details) VALUES (%s, %s, %s, %s, %s)",
        (username, ip, action, status, details)
    )
    mysql.connection.commit()
    cur.close()


def login_required(f):
    """Decorator: redirect to login if session is missing."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Decorator: block access unless user is admin."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Access denied. Admin role required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated


# ----------------------------------------------------------------
# Routes
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
            "SELECT u.*, r.role_name FROM users u JOIN roles r ON u.role_id = r.role_id WHERE u.username = %s AND u.is_active = TRUE",
            (username,)
        )
        user = cur.fetchone()

        if user and bcrypt.checkpw(password, user['password_hash'].encode('utf-8')):
            session['user_id']  = user['user_id']
            session['username'] = user['username']
            session['role']     = user['role_name']

            # Update last login timestamp
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


@app.route('/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor()

    # Summary counts
    cur.execute("SELECT COUNT(*) as total FROM users WHERE is_active = TRUE")
    total_users = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) as total FROM audit_log WHERE status = 'failed' AND DATE(logged_at) = CURDATE()")
    failed_today = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) as total FROM roles")
    total_roles = cur.fetchone()['total']

    # Recent audit log (last 10 entries)
    cur.execute("SELECT * FROM audit_log ORDER BY logged_at DESC LIMIT 10")
    recent_logs = cur.fetchall()

    cur.close()

    return render_template('dashboard.html',
                           total_users=total_users,
                           failed_today=failed_today,
                           total_roles=total_roles,
                           recent_logs=recent_logs)


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
    username  = request.form['username'].strip()
    email     = request.form['email'].strip()
    password  = request.form['password'].encode('utf-8')
    role_id   = request.form['role_id']

    password_hash = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

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


@app.route('/audit')
@login_required
@admin_required
def audit():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM audit_log ORDER BY logged_at DESC LIMIT 100")
    logs = cur.fetchall()
    cur.close()
    return render_template('audit.html', logs=logs)


if __name__ == '__main__':
    app.run(debug=True)
