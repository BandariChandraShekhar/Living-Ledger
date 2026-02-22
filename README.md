# 🔮 The Living Ledger

**AI-Driven Metadata Observability & Discovery Platform**

A comprehensive metadata management system with intelligent user authentication, admin controls, real-time session tracking, Gmail OTP, and Indian Standard Time support.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Gmail OTP Setup](#-gmail-otp-setup)
- [Usage](#-usage)
- [Deployment](#-deployment)
- [API Documentation](#-api-documentation)
- [Database Schema](#-database-schema)
- [Security](#-security)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🔐 Authentication System
- **Secure Login/Signup** with bcrypt password hashing
- **Email Validation** using Pydantic EmailStr
- **Gmail OTP for Password Reset** - Real email sending via SMTP
- **Session Tracking** with login/logout timestamps in IST
- **User Approval Workflow** - Admin must approve new signups
- **Indian Standard Time (IST)** - All timestamps in UTC+5:30

### 👨‍💼 Admin Dashboard
- **User Management** - Approve/reject pending users
- **Real-Time Monitoring** - Track active sessions
- **Login/Logout Activity** - Complete session history with:
  - User details (name, email, company, employee ID, department)
  - Login/logout timestamps (IST format)
  - IP addresses and user agents
- **Statistics Dashboard** - Total users, pending approvals, active sessions
- **Auto-Refresh** - Updates every 10 seconds
- **IST Timezone** - All times displayed in Indian Standard Time

### 📊 Metadata Management
- **Dashboard Overview** - Real-time metadata observability
- **Entity Management** - Create, certify, and deny metadata entities
- **Persistent Storage** - Entities saved in database (survive restart)
- **Statistical Analysis** - Automated data profiling
- **AI-Powered Descriptions** - Intelligent metadata enrichment
- **Drift Detection** - Proactive data quality monitoring
- **Search Functionality** - Natural language metadata search

### 🛡️ Security Features
- **Password Hashing** - bcrypt encryption with salt
- **Email Masking** - Privacy-first logging (e.g., "jo***@company.com")
- **Strong Password Requirements** - 8+ chars, uppercase, lowercase, number
- **Session Management** - Secure login/logout tracking
- **Admin Activity Logging** - Audit trail for all admin actions
- **Gmail SMTP SSL** - Secure email sending (port 465)

### 💾 Data Persistence
- **SQLite Database** - All data persists after restart
- **User Profiles** - Name, email, company, employee ID, department
- **Session History** - Complete login/logout records
- **OTP Storage** - Secure password reset codes with 10-minute expiration
- **Metadata Entities** - Processed entities stored permanently
- **Historical Metrics** - Statistical data tracking over time

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12 (recommended) or 3.11
- pip (Python package manager)
- Gmail account (for OTP emails)

### Installation (2 Minutes)

```bash
# 1. Navigate to project
cd living_ledger

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start server
python START.py
```

Server will start on **http://localhost:8000**

### Default Admin Credentials
```
Email: admin@livingledger.com
Password: Admin@123
```
⚠️ **Change this password immediately after first login!**

### First Login

1. Open http://localhost:8000
2. Login with admin credentials
3. You'll see the main dashboard
4. Click **shield icon** to access Admin Dashboard

---

## 📦 Installation

### Option 1: Quick Install

```bash
cd living_ledger
pip install -r requirements.txt
python START.py
```

### Option 2: Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
cd living_ledger
pip install -r requirements.txt

# Start server
python START.py
```

### Dependencies

```txt
fastapi==0.115.0          # Web framework
uvicorn[standard]==0.32.0 # ASGI server
pydantic==2.12.5          # Data validation
python-dotenv==1.0.0      # Environment variables
httpx==0.28.1             # HTTP client
bcrypt==4.2.1             # Password hashing
email-validator==2.2.0    # Email validation
google-generativeai==0.8.3 # AI features
pytz==2024.1              # Timezone support (IST)
```

---

## � Gmail OTP Setup

To enable real Gmail OTP sending for password reset:

### Step 1: Enable 2-Step Verification

1. Go to https://myaccount.google.com/security
2. Sign in with your Gmail account
3. Click "2-Step Verification"
4. Follow prompts to enable it

### Step 2: Generate App Password

1. Go to https://myaccount.google.com/apppasswords
2. Sign in if needed
3. Select app: **Mail**
4. Select device: **Other (Custom name)**
5. Enter name: **Living Ledger**
6. Click **Generate**
7. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

### Step 3: Configure Environment Variables

1. Create `.env` file in `living_ledger/` folder:

```env
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop
```

2. Replace with your actual credentials
3. Remove all spaces from app password

### Step 4: Restart Server

```bash
python START.py
```

### Test OTP Email

1. Go to http://localhost:8000
2. Click "Forgot password?"
3. Enter any registered email
4. Check that email's inbox for OTP
5. Professional HTML email will arrive within seconds

**Fallback:** If Gmail not configured, OTP prints to terminal.

**Detailed Guide:** See `living_ledger/GMAIL_SETUP.md`

---

## 💻 Usage

### For End Users

#### 1. Sign Up

1. Go to http://localhost:8000
2. Click "Sign up"
3. Fill in details:
   - First Name, Last Name
   - Email (validated)
   - Company Name
   - Employee ID (optional)
   - Department (optional)
   - Password (8+ chars, uppercase, lowercase, number)
4. Submit → Wait for admin approval

#### 2. Login

1. After admin approval, login with your credentials
2. Access the main dashboard
3. View and manage metadata entities

#### 3. Forgot Password

1. Click "Forgot password?"
2. Enter your registered email
3. Check your Gmail inbox for OTP
4. Enter OTP and new password
5. Login with new password

#### 4. Process Sample Database

1. Login to dashboard
2. Look for "Process Data Source" section
3. Database file: `sample_data.db`
4. Click "Process"
5. Wait for processing (~21 entities created)
6. Entities will appear in dashboard
7. **Entities persist after restart!**

### For Administrators

#### 1. Access Admin Dashboard

1. Login as admin
2. Click the **shield icon** in sidebar
3. Or go to: http://localhost:8000/admin.html

#### 2. Approve Users

1. View "Pending User Approvals" section
2. See user details (name, email, company, employee ID, department)
3. Click "Approve" or "Reject"

#### 3. Monitor Activity

1. View "Login/Logout Activity" section
2. See real-time sessions with IST timestamps
3. Track login/logout times
4. View IP addresses

#### 4. Manage Users

1. View "All Registered Users" section
2. See user status (Pending/Approved/Rejected)
3. Monitor active sessions
4. Dashboard auto-refreshes every 10 seconds

---

## 🌐 Deployment

### Deploy to Render.com (Recommended)

#### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/living-ledger.git
git push -u origin main
```

#### 2. Create Render Account

- Go to https://render.com
- Sign up with GitHub

#### 3. Deploy

1. Click "New +" → "Web Service"
2. Select your repository
3. Configure:
   ```
   Build Command: cd living_ledger && pip install -r requirements.txt
   Start Command: cd living_ledger && uvicorn api:app --host 0.0.0.0 --port $PORT
   ```
4. Add Environment Variables:
   ```
   GMAIL_USER=your-email@gmail.com
   GMAIL_APP_PASSWORD=your-16-char-password
   ```
5. Click "Create Web Service"

#### 4. Access Your Live App

```
https://your-app.onrender.com
```

**Detailed Guide:** See `DEPLOY_LIVE.md`

---

## 📚 API Documentation

### Authentication Endpoints

#### POST `/api/v1/auth/signup`
Create a new user account (pending approval)

**Request:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@company.com",
  "company": "Acme Corp",
  "employee_id": "EMP12345",
  "department": "Engineering",
  "password": "SecurePass123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Account created successfully! Please wait for admin approval.",
  "user": {
    "user_id": "user_1",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@company.com",
    "company": "Acme Corp",
    "status": "pending"
  }
}
```

#### POST `/api/v1/auth/login`
Login to existing account

**Request:**
```json
{
  "email": "john@company.com",
  "password": "SecurePass123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "user_id": "user_1",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@company.com",
    "company": "Acme Corp",
    "is_admin": false,
    "session_id": 123
  }
}
```

#### POST `/api/v1/auth/forgot-password`
Request OTP for password reset

**Request:**
```json
{
  "email": "john@company.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "OTP sent to your email"
}
```

**Note:** OTP sent to user's Gmail inbox. Expires in 10 minutes (IST).

#### POST `/api/v1/auth/reset-password`
Reset password using OTP

**Request:**
```json
{
  "email": "john@company.com",
  "otp": "123456",
  "new_password": "NewSecurePass123"
}
```

### Admin Endpoints

#### GET `/api/v1/admin/users/pending`
Get all pending user approvals

#### POST `/api/v1/admin/users/approve`
Approve a pending user

#### POST `/api/v1/admin/users/reject`
Reject a pending user

#### GET `/api/v1/admin/sessions/all`
Get all login/logout sessions with IST timestamps

#### GET `/api/v1/admin/stats`
Get system statistics

### Metadata Endpoints

#### POST `/api/v1/process`
Process a data source through TLL pipeline

#### GET `/api/v1/entities`
Get all metadata entities

#### GET `/api/v1/entities/{entity_id}`
Get specific metadata entity

#### POST `/api/v1/certify`
Certify a metadata entity

#### POST `/api/v1/deny`
Deny a metadata entity

---

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    company TEXT NOT NULL,
    employee_id TEXT,
    department TEXT,
    password_hash TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    is_admin INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    approved_at TEXT,
    approved_by TEXT
);
```

### Login Sessions Table
```sql
CREATE TABLE login_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    email TEXT NOT NULL,
    login_time TEXT NOT NULL,
    logout_time TEXT,
    ip_address TEXT,
    user_agent TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### Metadata Entities Table
```sql
CREATE TABLE metadata_entities (
    entity_id TEXT PRIMARY KEY,
    entity_data TEXT NOT NULL,
    certification_status TEXT DEFAULT 'uncertified',
    certified_by TEXT,
    certified_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    version INTEGER DEFAULT 1
);
```

### Historical Metrics Table
```sql
CREATE TABLE historical_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    column_id TEXT NOT NULL,
    metrics_data TEXT NOT NULL,
    calculated_at TEXT NOT NULL
);
```

---

## 🔒 Security

### Password Security
- **Hashing:** bcrypt with salt
- **Requirements:** 8+ characters, uppercase, lowercase, number
- **Storage:** Only hashed passwords in database
- **Verification:** Secure bcrypt.checkpw()

### Email Security
- **Validation:** Pydantic EmailStr validation
- **Masking:** Emails masked in logs (e.g., "jo***@company.com")
- **OTP:** 6-digit code, 10-minute expiration (IST)
- **SMTP:** SSL encryption (port 465)

### Session Security
- **Tracking:** Login/logout timestamps in IST
- **IP Logging:** IP addresses recorded
- **User Agent:** Browser information stored
- **Database:** All sessions persisted

### Admin Security
- **Approval Workflow:** New users require admin approval
- **Activity Logging:** All admin actions logged with IST timestamps
- **Access Control:** Admin-only routes protected
- **Default Account:** Must change password after first login

### Best Practices
1. ✅ Change default admin password immediately
2. ✅ Use strong passwords for all accounts
3. ✅ Enable HTTPS in production
4. ✅ Set up environment variables for secrets
5. ✅ Regular database backups
6. ✅ Monitor admin activity logs
7. ✅ Never commit `.env` file to Git

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'pytz'"

**Solution:**
```bash
pip install pytz==2024.1
```

### Issue: OTP not received in Gmail

**Solutions:**
1. Check spam folder
2. Verify `.env` file exists in `living_ledger/` folder
3. Check `GMAIL_USER` and `GMAIL_APP_PASSWORD` are correct
4. Remove spaces from app password
5. Restart server
6. Check terminal for error messages

**Fallback:** OTP will print to terminal if Gmail not configured

### Issue: Entities not showing after processing

**Solutions:**
1. Check terminal for processing errors
2. Verify `sample_data.db` exists
3. Check database: `living_ledger.db`
4. Entities now persist after restart (stored in database)

### Issue: Wrong timezone displayed

**Solutions:**
1. Verify `pytz==2024.1` is installed
2. Restart server
3. Clear browser cache
4. Check admin dashboard - should show "IST" suffix

### Issue: Port 8000 already in use

**Solution:**
Server automatically tries ports 8001, 8002, 8003 if 8000 is busy.

Or manually kill the process:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

### Issue: Login page not showing

**Solutions:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Open in incognito window (Ctrl+Shift+N)
3. Hard refresh (Ctrl+Shift+R)
4. Logout first if already logged in

**Detailed Guide:** See `TROUBLESHOOTING.md`

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

See `CONTRIBUTING.md` for detailed guidelines.

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎯 Features Summary

### ✅ Implemented Features

- ✅ User authentication with bcrypt
- ✅ Gmail OTP for password reset
- ✅ Indian Standard Time (IST) support
- ✅ Admin dashboard with user management
- ✅ Login/logout activity tracking
- ✅ Session management with IST timestamps
- ✅ Metadata entity processing
- ✅ Persistent storage (SQLite)
- ✅ Entity certification workflow
- ✅ Statistical analysis
- ✅ AI-powered descriptions
- ✅ Drift detection
- ✅ Search functionality

### 🚀 Roadmap

- [ ] PostgreSQL support for production
- [ ] Two-factor authentication (2FA)
- [ ] Role-based access control (RBAC)
- [ ] API rate limiting
- [ ] Comprehensive test suite
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Monitoring and logging (Sentry)
- [ ] Performance optimization
- [ ] Multi-language support

---

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check `TROUBLESHOOTING.md` for common issues
- See `living_ledger/GMAIL_SETUP.md` for Gmail configuration
- See `living_ledger/IST_TIMEZONE.md` for timezone details

---

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Pydantic for data validation
- bcrypt for secure password hashing
- Google Generative AI for metadata enrichment
- pytz for timezone support
- Font Awesome for icons
- The open-source community

---

## 📊 Project Statistics

- **Lines of Code:** ~5,000+
- **Files:** 15 Python files, 3 HTML files
- **Database Tables:** 7 tables
- **API Endpoints:** 20+ endpoints
- **Features:** 15+ major features
- **Documentation:** 5 guides

---

**Made with ❤️ for The Living Ledger**

⭐ Star this repo if you find it helpful!

🔗 **Live Demo:** Coming soon...

📧 **Official Email:** livingledger3@gmail.com (for OTP sending)

---

## 🎉 Quick Reference

### Start Server
```bash
cd living_ledger
python START.py
```

### Access Points
- **Main App:** http://localhost:8000
- **Admin Dashboard:** http://localhost:8000/admin.html
- **Login Page:** http://localhost:8000/auth.html

### Default Credentials
- **Email:** admin@livingledger.com
- **Password:** Admin@123

### Gmail OTP
- **Sender:** livingledger3@gmail.com
- **Config:** `living_ledger/.env`
- **Guide:** `living_ledger/GMAIL_SETUP.md`

### Database
- **File:** `living_ledger/living_ledger.db`
- **Sample Data:** `living_ledger/sample_data.db`
- **Tables:** 7 (users, sessions, entities, metrics, etc.)

---

**Version:** 1.0.0  
**Last Updated:** February 2026  
**Status:** ✅ Production Ready
