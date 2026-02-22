"""Database management for The Living Ledger"""
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import bcrypt
import pytz

# Indian Standard Time
IST = pytz.timezone('Asia/Kolkata')

def get_ist_time():
    """Get current time in IST"""
    return datetime.now(IST)

def get_ist_timestamp():
    """Get current timestamp in IST as string"""
    return get_ist_time().strftime('%Y-%m-%d %H:%M:%S')


class Database:
    """SQLite database manager for persistent storage"""
    
    def __init__(self, db_path: str = "living_ledger.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
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
            )
        ''')
        
        # Login sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                email TEXT NOT NULL,
                login_time TEXT NOT NULL,
                logout_time TEXT,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # OTP storage table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS otp_codes (
                email TEXT PRIMARY KEY,
                otp TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Admin activity log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_activity (
                activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id TEXT NOT NULL,
                action TEXT NOT NULL,
                target_user_id TEXT,
                details TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (admin_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        
        # Create default admin if not exists
        self.create_default_admin()
        
        conn.close()
    
    def create_default_admin(self):
        """Create default admin account"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if admin exists
        cursor.execute("SELECT user_id FROM users WHERE is_admin = 1")
        if cursor.fetchone():
            conn.close()
            return
        
        # Create admin account
        admin_password = "Admin@123"  # Default password
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), salt).decode('utf-8')
        
        cursor.execute('''
            INSERT INTO users (
                user_id, email, first_name, last_name, company,
                password_hash, status, is_admin, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'admin_1',
            'admin@livingledger.com',
            'Admin',
            'User',
            'Living Ledger',
            password_hash,
            'approved',
            1,
            get_ist_timestamp()
        ))
        
        conn.commit()
        conn.close()
        
        print("\n" + "="*60)
        print("🔑 DEFAULT ADMIN ACCOUNT CREATED")
        print("="*60)
        print("Email: admin@livingledger.com")
        print("Password: Admin@123")
        print("⚠️  CHANGE THIS PASSWORD AFTER FIRST LOGIN!")
        print("="*60 + "\n")
    
    # User operations
    def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (
                user_id, email, first_name, last_name, company,
                employee_id, department, password_hash, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_data['user_id'],
            user_data['email'],
            user_data['first_name'],
            user_data['last_name'],
            user_data['company'],
            user_data.get('employee_id'),
            user_data.get('department'),
            user_data['password_hash'],
            'pending',
            get_ist_timestamp()
        ))
        
        conn.commit()
        conn.close()
        return user_data['user_id']
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_users(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all users, optionally filtered by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute("SELECT * FROM users WHERE status = ? ORDER BY created_at DESC", (status,))
        else:
            cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def approve_user(self, user_id: str, admin_id: str) -> bool:
        """Approve a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET status = 'approved', approved_at = ?, approved_by = ?
            WHERE user_id = ?
        ''', (get_ist_timestamp(), admin_id, user_id))
        
        # Log admin activity
        cursor.execute('''
            INSERT INTO admin_activity (admin_id, action, target_user_id, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (admin_id, 'approve_user', user_id, get_ist_timestamp()))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    def reject_user(self, user_id: str, admin_id: str, reason: str = None) -> bool:
        """Reject a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET status = 'rejected'
            WHERE user_id = ?
        ''', (user_id,))
        
        # Log admin activity
        details = f"Reason: {reason}" if reason else None
        cursor.execute('''
            INSERT INTO admin_activity (admin_id, action, target_user_id, details, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (admin_id, 'reject_user', user_id, details, get_ist_timestamp()))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    # Login session operations
    def create_login_session(self, user_id: str, email: str, ip_address: str = None, user_agent: str = None) -> int:
        """Create a login session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO login_sessions (user_id, email, login_time, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, email, get_ist_timestamp(), ip_address, user_agent))
        
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return session_id
    
    def end_login_session(self, session_id: int) -> bool:
        """End a login session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE login_sessions 
            SET logout_time = ?
            WHERE session_id = ? AND logout_time IS NULL
        ''', (get_ist_timestamp(), session_id))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.*, u.first_name, u.last_name, u.company, u.employee_id, u.department
            FROM login_sessions s
            JOIN users u ON s.user_id = u.user_id
            WHERE s.logout_time IS NULL
            ORDER BY s.login_time DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_all_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all sessions (active and past)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.*, u.first_name, u.last_name, u.company, u.employee_id, u.department
            FROM login_sessions s
            JOIN users u ON s.user_id = u.user_id
            ORDER BY s.login_time DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_user_sessions(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's recent sessions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM login_sessions
            WHERE user_id = ?
            ORDER BY login_time DESC
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # OTP operations
    def store_otp(self, email: str, otp: str, expires_at: str):
        """Store OTP for password reset"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO otp_codes (email, otp, expires_at, created_at)
            VALUES (?, ?, ?, ?)
        ''', (email, otp, expires_at, get_ist_timestamp()))
        
        conn.commit()
        conn.close()
    
    def get_otp(self, email: str) -> Optional[Dict[str, Any]]:
        """Get OTP for email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM otp_codes WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def delete_otp(self, email: str):
        """Delete OTP after use"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM otp_codes WHERE email = ?", (email,))
        conn.commit()
        conn.close()
    
    # Admin operations
    def get_admin_activity(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent admin activity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.*, u.first_name, u.last_name, u.email
            FROM admin_activity a
            JOIN users u ON a.admin_id = u.user_id
            ORDER BY a.timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total users
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_admin = 0")
        total_users = cursor.fetchone()['count']
        
        # Pending users
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE status = 'pending'")
        pending_users = cursor.fetchone()['count']
        
        # Approved users
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE status = 'approved'")
        approved_users = cursor.fetchone()['count']
        
        # Active sessions
        cursor.execute("SELECT COUNT(*) as count FROM login_sessions WHERE logout_time IS NULL")
        active_sessions = cursor.fetchone()['count']
        
        # Total logins today
        today = get_ist_time().date().isoformat()
        cursor.execute("SELECT COUNT(*) as count FROM login_sessions WHERE DATE(login_time) = ?", (today,))
        logins_today = cursor.fetchone()['count']
        
        conn.close()
        
        return {
            "total_users": total_users,
            "pending_users": pending_users,
            "approved_users": approved_users,
            "active_sessions": active_sessions,
            "logins_today": logins_today
        }


# Global database instance
db = Database()
