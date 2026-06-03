# User Authentication & Access Control System

A role-based access control system with login auditing built with MySQL, Python Flask, and HTML.

## Stack
- **Database**: MySQL
- **Backend**: Python Flask
- **Frontend**: HTML + CSS (dark theme, no external UI library)

## Features
- Secure login with bcrypt password hashing
- Role-based access (Admin, Editor, Viewer)
- User management (create, enable/disable accounts)
- Full audit log of every login attempt and admin action
- Clean dark dashboard

## Setup

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
Edit `app.py` and update:
```python
app.config['MYSQL_PASSWORD'] = 'your_mysql_password'
```

### 4. Set admin password
```bash
python setup_admin.py
```

### 5. Run the app
```bash
python app.py
```

Open: http://localhost:5000

## Default Login
- Username: `admin`
- Password: `Admin@1234`

## Project Structure
```
access-control-system/
├── app.py                  # Flask application
├── setup_admin.py          # One-time admin setup
├── requirements.txt
├── database/
│   ├── schema.sql          # Table definitions
│   └── seed.sql            # Default roles and admin user
└── templates/
    ├── base.html           # Shared layout with sidebar
    ├── login.html          # Login page
    ├── dashboard.html      # Overview + recent activity
    ├── users.html          # User management (admin only)
    └── audit.html          # Full audit log (admin only)
```

## Database Schema

| Table | Purpose |
|---|---|
| roles | Permission level definitions |
| users | System accounts |
| permissions | What each role can access |
| audit_log | Every login attempt and action |

## Author
Fadi Amir — GitHub: github.com/unreallfadi
