# Multi-User Database Access Control System

A DBA-grade database access control system built with MySQL, Python Flask, and HTML.
Manages system users, database-level privileges, audit logging, and generates exportable permissions reports.

---

## Features

- Secure login with bcrypt password hashing
- Password policy enforcement (length, number, special character)
- Role-based access control (Admin, Editor, Viewer)
- User management — create, enable/disable, reset passwords
- **MySQL GRANT / REVOKE privilege management**
- **Permissions report** (schema-level and table-level)
- **CSV export** of full permissions report
- **Database health stats** — table sizes and row counts
- Full audit log of every login, action, and privilege change

---

## Tech Stack

| Layer    | Technology           |
|----------|----------------------|
| Backend  | Python, Flask        |
| Database | MySQL                |
| Frontend | HTML5, CSS3          |
| Security | bcrypt, session auth |

---

## Project Structure

```
access-control-system/
├── app.py                  # Flask application — all routes and logic
├── setup_admin.py          # One-time admin account setup
├── requirements.txt
├── database/
│   ├── schema.sql          # Table definitions and indexes
│   └── seed.sql            # Default roles and permissions
└── templates/
    ├── base.html           # Shared dark layout and sidebar
    ├── login.html          # Login page
    ├── dashboard.html      # Overview, DB health, recent activity
    ├── users.html          # User management
    ├── privileges.html     # MySQL GRANT / REVOKE
    ├── report.html         # Permissions report with CSV export
    └── audit.html          # Full audit log
```

---

## Database Schema

| Table       | Purpose                                    |
|-------------|--------------------------------------------|
| roles       | Role definitions (admin, editor, viewer)   |
| users       | System accounts linked to roles            |
| permissions | Resource access per role                   |
| audit_log   | Every login, action, and privilege change  |

---

## Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Create the database

```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed.sql
```

### 3. Configure database connection

Edit `app.py`:

```python
app.config['MYSQL_PASSWORD'] = 'your_mysql_password'
```

### 4. Create admin account

```bash
python setup_admin.py
```

### 5. Run the application

```bash
python app.py
```

Open: [http://localhost:5000](http://localhost:5000)

---

## API Routes

| Route                              | Method | Access | Description                    |
|------------------------------------|--------|--------|--------------------------------|
| `/`                                | GET    | All    | Redirect to dashboard or login |
| `/login`                           | GET/POST | All  | Login page                     |
| `/logout`                          | GET    | Auth   | End session                    |
| `/dashboard`                       | GET    | Auth   | Overview and DB health         |
| `/users`                           | GET    | Admin  | User list                      |
| `/users/create`                    | POST   | Admin  | Create new user                |
| `/users/toggle/<id>`               | POST   | Admin  | Enable/disable user            |
| `/users/reset-password/<id>`       | POST   | Admin  | Reset user password            |
| `/privileges`                      | GET    | Admin  | Privilege management page      |
| `/privileges/grant`                | POST   | Admin  | GRANT privilege                |
| `/privileges/revoke`               | POST   | Admin  | REVOKE privilege               |
| `/report`                          | GET    | Admin  | Permissions report             |
| `/report/export`                   | GET    | Admin  | Download CSV report            |
| `/audit`                           | GET    | Admin  | Full audit log                 |

---

## Author

**Fadi**

SQL Developer | Database Design | Web Design

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://linkedin.com)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black)](https://github.com)
