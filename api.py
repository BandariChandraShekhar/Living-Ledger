"""FastAPI REST API for The Living Ledger"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import os
import bcrypt
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()

from main import LivingLedger
from models import DataSourceConfig, CertificationStatus
from database import db
from admin_endpoints import router as admin_router
# Get base directory for file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Indian Standard Time
IST = pytz.timezone('Asia/Kolkata')

def get_ist_time():
    """Get current time in IST"""
    return datetime.now(IST)

app = FastAPI(
    title="The Living Ledger",
    description="Autonomous AI-Driven Metadata Observability & Discovery Platform",
    version="1.0.0"
)

# Include admin router
app.include_router(admin_router)

# Mount static files
static_dir = os.path.join(BASE_DIR, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Living Ledger
tll = LivingLedger()


# Request/Response Models
class ProcessDataSourceRequest(BaseModel):
    connection_string: str
    source_type: str = "sqlite"
    sampling_rate: float = 0.1
    max_sample_size: int = 10000


class SearchRequest(BaseModel):
    query: str
    limit: int = 10


class CertifyRequest(BaseModel):
    entity_id: str
    user_id: str
    notes: Optional[str] = None


class UncertifyRequest(BaseModel):
    entity_id: str
    user_id: str
    notes: Optional[str] = None


class DenyRequest(BaseModel):
    entity_id: str
    user_id: str
    notes: Optional[str] = None


class CreateEntityRequest(BaseModel):
    table_name: str
    column_name: str
    data_type: str
    business_name: str
    description: str
    business_domain: str
    nullable: bool = True


class AcknowledgeAlertRequest(BaseModel):
    alert_id: str
    user_id: str
    notes: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    company: str
    employee_id: Optional[str] = None
    department: Optional[str] = None
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str


class ApproveUserRequest(BaseModel):
    user_id: str
    admin_id: str


class RejectUserRequest(BaseModel):
    user_id: str
    admin_id: str
    reason: Optional[str] = None


# Active sessions tracking (in-memory for session IDs)
active_user_sessions: Dict[str, int] = {}


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    
    return True, "Password is strong"


def mask_email(email: str) -> str:
    """Mask email for logging (show only first 2 chars and domain)"""
    if '@' not in email:
        return "***"
    local, domain = email.split('@')
    if len(local) <= 2:
        return f"{local[0]}***@{domain}"
    return f"{local[:2]}***@{domain}"


def generate_otp():
    """Generate a 6-digit OTP"""
    import random
    return str(random.randint(100000, 999999))


def send_otp_email(email, otp):
    """Send OTP via Gmail"""
    try:
        # Get Gmail credentials from environment variables
        gmail_user = os.getenv('GMAIL_USER')
        gmail_password = os.getenv('GMAIL_APP_PASSWORD')
        
        if not gmail_user or not gmail_password:
            # Fallback to terminal if credentials not configured
            print(f"\n{'='*60}")
            print(f"⚠️  Gmail not configured! OTP printed to terminal:")
            print(f"{'='*60}")
            print(f"📧 EMAIL: {email}")
            print(f"🔑 OTP: {otp}")
            print(f"{'='*60}\n")
            return True
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Password Reset OTP - The Living Ledger'
        msg['From'] = gmail_user
        msg['To'] = email
        
        # HTML email body
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
              <h2 style="color: #6366f1; margin-bottom: 20px;">🔐 Password Reset Request</h2>
              <p style="font-size: 16px; color: #333; line-height: 1.6;">
                You requested to reset your password for The Living Ledger.
              </p>
              <div style="background-color: #f0f0f0; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center;">
                <p style="font-size: 14px; color: #666; margin-bottom: 10px;">Your OTP code is:</p>
                <h1 style="color: #6366f1; font-size: 36px; letter-spacing: 8px; margin: 10px 0;">{otp}</h1>
              </div>
              <p style="font-size: 14px; color: #666; line-height: 1.6;">
                ⏰ This code will expire in <strong>10 minutes</strong>.
              </p>
              <p style="font-size: 14px; color: #666; line-height: 1.6;">
                If you didn't request this, please ignore this email.
              </p>
              <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 30px 0;">
              <p style="font-size: 12px; color: #999; text-align: center;">
                The Living Ledger - AI-Driven Metadata Observability Platform
              </p>
            </div>
          </body>
        </html>
        """
        
        # Attach HTML content
        msg.attach(MIMEText(html, 'html'))
        
        # Send email via Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_user, gmail_password)
            server.send_message(msg)
        
        print(f"\n{'='*60}")
        print(f"✅ OTP EMAIL SENT SUCCESSFULLY")
        print(f"{'='*60}")
        print(f"To: {email}")
        print(f"OTP: {otp}")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ ERROR SENDING EMAIL: {str(e)}")
        print(f"{'='*60}")
        print(f"📧 EMAIL: {email}")
        print(f"🔑 OTP: {otp}")
        print(f"{'='*60}\n")
        # Return True anyway so user can still use the OTP
        return True


# API Endpoints
@app.get("/")
@app.head("/")
async def root():
    """Redirect to login page"""
    auth_path = os.path.join(BASE_DIR, "static", "auth.html")
    if os.path.exists(auth_path):
        return FileResponse(auth_path)
    return {
        "name": "The Living Ledger",
        "version": "1.0.0",
        "description": "Autonomous AI-Driven Metadata Observability Platform"
    }



@app.get("/auth.html")
async def serve_auth():
    """Serve the authentication page"""
    auth_path = os.path.join(BASE_DIR, "static", "auth.html")
    if os.path.exists(auth_path):
        return FileResponse(auth_path)
    raise HTTPException(status_code=404, detail="Authentication page not found")


@app.get("/pro.html")
async def serve_dashboard():
    """Serve the dashboard (after login)"""
    pro_path = os.path.join(BASE_DIR, "static", "pro.html")
    if os.path.exists(pro_path):
        return FileResponse(pro_path)
    raise HTTPException(status_code=404, detail="Dashboard not found")


@app.get("/admin.html")
async def serve_admin():
    """Serve the admin dashboard"""
    admin_path = os.path.join(BASE_DIR, "static", "admin.html")
    if os.path.exists(admin_path):
        return FileResponse(admin_path)
    raise HTTPException(status_code=404, detail="Admin dashboard not found")


# Authentication Endpoints
@app.post("/api/v1/auth/signup")
async def signup(request: SignupRequest):
    """Create a new user account (pending approval)"""
    print(f"\n{'='*60}")
    print(f"📝 SIGNUP REQUEST")
    print(f"{'='*60}")
    print(f"Email: {mask_email(request.email)}")
    print(f"Name: {request.first_name} {request.last_name}")
    print(f"Company: {request.company}")
    print(f"Employee ID: {request.employee_id or 'Not provided'}")
    print(f"Department: {request.department or 'Not provided'}")
    
    # Check if user already exists
    existing_user = db.get_user_by_email(request.email)
    if existing_user:
        print(f"❌ Email already registered!")
        print(f"{'='*60}\n")
        return {
            "success": False,
            "message": "Email already registered"
        }
    
    # Validate password strength
    is_valid, message = validate_password_strength(request.password)
    if not is_valid:
        print(f"❌ Weak password: {message}")
        print(f"{'='*60}\n")
        return {
            "success": False,
            "message": message
        }
    
    # Hash the password
    password_hash = hash_password(request.password)
    
    # Create user
    user_count = len(db.get_all_users())
    user_id = f"user_{user_count + 1}"
    
    user_data = {
        "user_id": user_id,
        "first_name": request.first_name,
        "last_name": request.last_name,
        "email": request.email,
        "company": request.company,
        "employee_id": request.employee_id,
        "department": request.department,
        "password_hash": password_hash
    }
    
    db.create_user(user_data)
    
    print(f"✅ User created successfully!")
    print(f"User ID: {user_id}")
    print(f"Status: PENDING APPROVAL")
    print(f"Password: HASHED (secure)")
    print(f"{'='*60}\n")
    
    return {
        "success": True,
        "message": "Account created successfully! Please wait for admin approval.",
        "user": {
            "user_id": user_id,
            "first_name": request.first_name,
            "last_name": request.last_name,
            "email": request.email,
            "company": request.company,
            "status": "pending"
        }
    }


@app.post("/api/v1/auth/login")
async def login(request: LoginRequest, req: Request):
    """Login to existing account"""
    print(f"\n{'='*60}")
    print(f"🔐 LOGIN REQUEST")
    print(f"{'='*60}")
    print(f"Email: {mask_email(request.email)}")
    
    # Check if user exists
    user = db.get_user_by_email(request.email)
    if not user:
        print(f"❌ User not found!")
        print(f"{'='*60}\n")
        return {
            "success": False,
            "message": "Invalid email or password"
        }
    
    # Check if user is approved
    if user['status'] == 'pending':
        print(f"⏳ User pending approval!")
        print(f"{'='*60}\n")
        return {
            "success": False,
            "message": "Your account is pending admin approval. Please wait."
        }
    
    if user['status'] == 'rejected':
        print(f"❌ User rejected!")
        print(f"{'='*60}\n")
        return {
            "success": False,
            "message": "Your account has been rejected. Please contact admin."
        }
    
    # Verify password hash
    if not verify_password(request.password, user["password_hash"]):
        print(f"❌ Invalid password!")
        print(f"{'='*60}\n")
        return {
            "success": False,
            "message": "Invalid email or password"
        }
    
    # Create login session
    ip_address = req.client.host if req.client else None
    user_agent = req.headers.get("user-agent")
    session_id = db.create_login_session(user['user_id'], user['email'], ip_address, user_agent)
    
    # Store session ID for logout
    active_user_sessions[user['user_id']] = session_id
    
    print(f"✅ Login successful!")
    print(f"User: {user['first_name']} {user['last_name']}")
    print(f"Session ID: {session_id}")
    print(f"{'='*60}\n")
    
    return {
        "success": True,
        "message": "Login successful",
        "user": {
            "user_id": user["user_id"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"],
            "company": user["company"],
            "is_admin": bool(user["is_admin"]),
            "session_id": session_id
        }
    }


@app.post("/api/v1/auth/logout")
async def logout(user_id: str):
    """Logout and end session"""
    print(f"\n{'='*60}")
    print(f"🚪 LOGOUT REQUEST")
    print(f"{'='*60}")
    print(f"User ID: {user_id}")
    
    # End the session
    if user_id in active_user_sessions:
        session_id = active_user_sessions[user_id]
        db.end_login_session(session_id)
        del active_user_sessions[user_id]
        print(f"✅ Session ended: {session_id}")
    
    print(f"{'='*60}\n")
    
    return {
        "success": True,
        "message": "Logged out successfully"
    }


@app.post("/api/v1/auth/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Send OTP to user's email for password reset"""
    print(f"\n{'='*60}")
    print(f"🔑 FORGOT PASSWORD REQUEST")
    print(f"{'='*60}")
    print(f"Email: {mask_email(request.email)}")
    
    # Check if user exists
    user = db.get_user_by_email(request.email)
    if not user:
        print(f"❌ User not found!")
        print(f"{'='*60}\n")
        return {
            "success": False,
            "message": "Email not found"
        }
    
    # Generate OTP
    otp = generate_otp()
    
    # Store OTP with timestamp (expires in 10 minutes) - IST
    expires_at = (get_ist_time() + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')
    db.store_otp(request.email, otp, expires_at)
    
    # Send OTP via email
    send_otp_email(request.email, otp)
    
    print(f"✅ OTP generated and sent!")
    print(f"OTP: {otp}")
    print(f"Expires in: 10 minutes (IST)")
    print(f"{'='*60}\n")
    
    return {
        "success": True,
        "message": "OTP sent to your email"
    }


@app.post("/api/v1/auth/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset password using OTP"""
    print(f"\n{'='*60}")
    print(f"🔄 PASSWORD RESET REQUEST")
    print(f"{'='*60}")
    print(f"Email: {mask_email(request.email)}")
    
    # Check if user exists
    user = db.get_user_by_email(request.email)
    if not user:
        print(f"❌ User not found!")
        print(f"{'='*60}\n")
        return {
            "success": False,
            "message": "Email not found"
        }
    
    # Check if OTP exists
    otp_data = db.get_otp(request.email)
    if not otp_data:
        print(f"❌ No OTP found!")
        print(f"{'='*60}\n")
        return {
            "success": False,
            "message": "No OTP found. Please request a new one."
        }
    
    # Check if OTP is expired (IST)
    expires_at = datetime.strptime(otp_data["expires_at"], '%Y-%m-%d %H:%M:%S')
    expires_at = IST.localize(expires_at)
    if get_ist_time() > expires_at:
        db.delete_otp(request.email)
        print(f"❌ OTP expired!")
        print(f"{'='*60}\n")
        return {
            "success": False,
            "message": "OTP expired. Please request a new one."
        }
    
    # Verify OTP
    if otp_data["otp"] != request.otp:
        print(f"❌ Invalid OTP!")
        print(f"{'='*60}\n")
        return {
            "success": False,
            "message": "Invalid OTP"
        }
    
    # Validate new password strength
    is_valid, message = validate_password_strength(request.new_password)
    if not is_valid:
        print(f"❌ Weak password: {message}")
        print(f"{'='*60}\n")
        return {
            "success": False,
            "message": message
        }
    
    # Hash and update password
    password_hash = hash_password(request.new_password)
    
    # Update password in database
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password_hash = ? WHERE email = ?",
        (password_hash, request.email)
    )
    conn.commit()
    conn.close()
    
    # Clear OTP
    db.delete_otp(request.email)
    
    print(f"✅ Password reset successful!")
    print(f"New password: HASHED (secure)")
    print(f"{'='*60}\n")
    
    return {
        "success": True,
        "message": "Password reset successful"
    }


@app.get("/index.html")
async def serve_index():
    """Serve index.html directly"""
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="index.html not found")


@app.get("/simple")
async def serve_simple():
    """Serve simple test page"""
    simple_path = os.path.join("static", "simple.html")
    if os.path.exists(simple_path):
        return FileResponse(simple_path)
    raise HTTPException(status_code=404, detail="simple.html not found")


@app.post("/api/v1/process")
async def process_data_source(request: ProcessDataSourceRequest):
    """Process a data source through the TLL pipeline"""
    config = DataSourceConfig(
        connection_string=request.connection_string,
        source_type=request.source_type,
        sampling_rate=request.sampling_rate,
        max_sample_size=request.max_sample_size
    )
    
    results = await tll.process_data_source(config)
    return results


@app.post("/api/v1/search")
async def search_metadata(request: SearchRequest):
    """Search for metadata entities using natural language"""
    entities = await tll.search(request.query, request.limit)
    
    return {
        "query": request.query,
        "total_count": len(entities),
        "results": [
            {
                "entity_id": e.entity_id,
                "table_name": e.schema_metadata.table_name,
                "column_name": e.schema_metadata.column_name,
                "business_name": e.semantic_description.business_name,
                "description": e.semantic_description.description,
                "business_domain": e.semantic_description.business_domain,
                "data_type": e.schema_metadata.data_type,
                "certification_status": e.certification_status.value,
                "confidence_score": e.semantic_description.confidence_score,
                "example_values": e.semantic_description.example_values,
                "usage_guidelines": e.semantic_description.usage_guidelines,
                "statistics": {
                    "distinct_count": e.statistical_metrics.distinct_count,
                    "null_percentage": e.statistical_metrics.null_percentage,
                    "entropy": e.statistical_metrics.entropy,
                    "distribution_type": e.statistical_metrics.distribution_type
                }
            }
            for e in entities
        ]
    }


@app.get("/api/v1/entities")
async def get_all_entities(certified_only: bool = False):
    """Get all metadata entities"""
    entities = await tll.get_all_entities()
    
    # Filter for certified only if requested
    if certified_only:
        entities = [e for e in entities if e.certification_status.value == "certified"]
    
    return {
        "total_count": len(entities),
        "entities": [
            {
                "entity_id": e.entity_id,
                "table_name": e.schema_metadata.table_name,
                "column_name": e.schema_metadata.column_name,
                "business_name": e.semantic_description.business_name,
                "description": e.semantic_description.description,
                "business_domain": e.semantic_description.business_domain,
                "data_type": e.schema_metadata.data_type,
                "certification_status": e.certification_status.value,
                "confidence_score": e.semantic_description.confidence_score,
                "example_values": e.semantic_description.example_values,
                "usage_guidelines": e.semantic_description.usage_guidelines,
                "statistics": {
                    "distinct_count": e.statistical_metrics.distinct_count,
                    "null_percentage": e.statistical_metrics.null_percentage,
                    "entropy": e.statistical_metrics.entropy,
                    "distribution_type": e.statistical_metrics.distribution_type
                }
            }
            for e in entities
        ]
    }


@app.get("/api/v1/entities/{entity_id}")
async def get_entity(entity_id: str):
    """Get a specific metadata entity"""
    entity = await tll.get_entity(entity_id)
    
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return {
        "entity_id": entity.entity_id,
        "schema": {
            "table_name": entity.schema_metadata.table_name,
            "column_name": entity.schema_metadata.column_name,
            "data_type": entity.schema_metadata.data_type,
            "nullable": entity.schema_metadata.nullable,
            "constraints": entity.schema_metadata.constraints
        },
        "semantic": {
            "business_name": entity.semantic_description.business_name,
            "description": entity.semantic_description.description,
            "business_domain": entity.semantic_description.business_domain,
            "example_values": entity.semantic_description.example_values,
            "usage_guidelines": entity.semantic_description.usage_guidelines,
            "confidence_score": entity.semantic_description.confidence_score
        },
        "statistics": {
            "mean": entity.statistical_metrics.mean,
            "std_dev": entity.statistical_metrics.std_dev,
            "entropy": entity.statistical_metrics.entropy,
            "distinct_count": entity.statistical_metrics.distinct_count,
            "null_percentage": entity.statistical_metrics.null_percentage,
            "distribution_type": entity.statistical_metrics.distribution_type,
            "min_value": entity.statistical_metrics.min_value,
            "max_value": entity.statistical_metrics.max_value
        },
        "certification": {
            "status": entity.certification_status.value,
            "certified_by": entity.certified_by,
            "certified_at": entity.certified_at.isoformat() if entity.certified_at else None
        },
        "metadata": {
            "version": entity.version,
            "created_at": entity.created_at.isoformat(),
            "updated_at": entity.updated_at.isoformat()
        }
    }


@app.post("/api/v1/certify")
async def certify_entity(request: CertifyRequest):
    """Certify a metadata entity"""
    success = await tll.certify(request.entity_id, request.user_id, request.notes)
    
    if not success:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return {
        "success": True,
        "entity_id": request.entity_id,
        "certified_by": request.user_id,
        "certified_at": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/uncertify")
async def uncertify_entity(request: UncertifyRequest):
    """Uncertify a metadata entity"""
    success = await tll.uncertify(request.entity_id, request.user_id, request.notes)
    
    if not success:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return {
        "success": True,
        "entity_id": request.entity_id,
        "uncertified_by": request.user_id,
        "uncertified_at": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/deny")
async def deny_entity(request: DenyRequest):
    """Deny a metadata entity"""
    success = await tll.deny(request.entity_id, request.user_id, request.notes)
    
    if not success:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return {
        "success": True,
        "entity_id": request.entity_id,
        "denied_by": request.user_id,
        "denied_at": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/entities")
async def create_entity(request: CreateEntityRequest):
    """Manually create a new metadata entity"""
    try:
        entity_id = await tll.create_entity(
            table_name=request.table_name,
            column_name=request.column_name,
            data_type=request.data_type,
            business_name=request.business_name,
            description=request.description,
            business_domain=request.business_domain,
            nullable=request.nullable
        )
        
        return {
            "success": True,
            "entity_id": entity_id,
            "created_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        print(f"Error creating entity: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create entity: {str(e)}")


@app.get("/api/v1/drift-alerts")
async def get_drift_alerts(severity: Optional[str] = None):
    """Get active drift alerts"""
    alerts = await tll.get_drift_alerts(severity)
    
    return {
        "total_count": len(alerts),
        "alerts": [
            {
                "alert_id": a.alert_id,
                "column_id": a.column_id,
                "metric_name": a.metric_name,
                "previous_value": a.previous_value,
                "current_value": a.current_value,
                "drift_percentage": a.drift_percentage,
                "severity": a.severity,
                "detected_at": a.detected_at.isoformat(),
                "acknowledged": a.acknowledged
            }
            for a in alerts
        ]
    }


@app.post("/api/v1/drift-alerts/acknowledge")
async def acknowledge_alert(request: AcknowledgeAlertRequest):
    """Acknowledge a drift alert"""
    success = await tll.acknowledge_alert(request.alert_id, request.user_id, request.notes)
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {
        "success": True,
        "alert_id": request.alert_id,
        "acknowledged_by": request.user_id,
        "acknowledged_at": datetime.utcnow().isoformat()
    }


@app.get("/api/v1/stats")
async def get_stats():
    """Get platform statistics"""
    stats = await tll.get_stats()
    return stats


if __name__ == "__main__":
    import uvicorn
    import sys
    
    # Try port 8000 first, then 8001, 8002, etc.
    for port in [8000, 8001, 8002, 8003]:
        try:
            print(f"\n{'='*60}")
            print(f"Starting Living Ledger on port {port}...")
            print(f"{'='*60}\n")
            uvicorn.run(app, host="0.0.0.0", port=port)
            break
        except OSError as e:
            if "address already in use" in str(e).lower() or "10048" in str(e):
                print(f"Port {port} is already in use, trying next port...")
                continue
            else:
                raise




