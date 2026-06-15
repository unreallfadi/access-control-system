# User Authentication & Access Control System

> Role-based access control system with login auditing, built with Python Flask and MySQL.
> Demonstrates secure authentication design, privilege management, and audit trail implementation.

---

## Overview

This project simulates a real-world user management system with three access levels.
Every login attempt and admin action is logged to a full audit trail stored in MySQL.

---

## Features

| Feature | Description |
|---|---|
| Secure Login | bcrypt password hashing, no plaintext storage |
| Role-Based Access | Admin, Editor, and Viewer permission levels |
| User Management | Create, enable, and disable user accounts |
| Audit Log | Every login attempt and admin action is recorded |
| Session Control | Flask session management with login/logout flow |
| Dark Dashboard | Clean dark UI with no external CSS framework |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| Database | MySQL 8.0 |
| Auth | bcrypt, Flask sessions |
| Frontend | HTML5, CSS3 (dark theme) |

---

## Project Structure

```
access-control-system/
├── app.py              # Flask application and route handlers
├── setup_admin.py      # One-time admin account setup script
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore
├── database/
│   ├── schema.sql      # Table definitions and constraints
│   └── seed.sql        # Default roles and initial data
└── templates/
    ├── base.html       # Shared layout with sidebar navigation
    ├── login.html      # Login page
    ├── dashboard.html  # Overview with KPIs and recent activity
    ├── users.html      # User management (admin only)
    └── audit.html      # Full audit log viewer (admin only)
```

---

## Database Schema

| Table | Purpose |
|---|---|
| `roles` | Permission level definitions |
| `users` | System accounts with role assignment |
| `permissions` | What each role is allowed to access |
| `audit_log` | Full record of every login and admin action |

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/unreallfadi/access-control-system.git
cd access-control-system
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env and set your MySQL password and secret key
```

### 4. Create the database

```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed.sql
```

### 5. Set the admin password

```bash
python setup_admin.py
```

### 6. Run the application

```bash
python app.py
```

Open in browser: `http://localhost:5000`

---

## Access Roles

| Role | Permissions |
|---|---|
| Admin | Full access: user management, audit log, dashboard |
| Editor | Dashboard access only |
| Viewer | Dashboard access only (read-only) |

---

## Skills Demonstrated

- Secure password hashing with bcrypt
- Role-based access control (RBAC) design
- MySQL schema design with foreign key constraints
- Flask session management and route decorators
- Audit logging for compliance and traceability
- Environment variable management for sensitive config

---

## Author

**Fadi Amir**
Data Analyst | SQL Developer | Database Design

[![GitHub](https://img.shields.io/badge/GitHub-unreallfadi-181717?style=flat&logo=github)](https://github.com/unreallfadi)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-fadi--amir-0A66C2?style=flat&logo=linkedin)](https://www.linkedin.com/in/unreallfadi)
