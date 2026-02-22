"""Admin-specific API endpoints"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from database import db

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


class ApproveUserRequest(BaseModel):
    user_id: str
    admin_id: str


class RejectUserRequest(BaseModel):
    user_id: str
    admin_id: str
    reason: Optional[str] = None


@router.get("/users/pending")
async def get_pending_users():
    """Get all pending users"""
    users = db.get_all_users(status='pending')
    return {
        "success": True,
        "count": len(users),
        "users": [
            {
                "user_id": u["user_id"],
                "email": u["email"],
                "first_name": u["first_name"],
                "last_name": u["last_name"],
                "company": u["company"],
                "employee_id": u["employee_id"],
                "department": u["department"],
                "created_at": u["created_at"],
                "status": u["status"]
            }
            for u in users
        ]
    }


@router.get("/users/all")
async def get_all_users():
    """Get all users"""
    users = db.get_all_users()
    return {
        "success": True,
        "count": len(users),
        "users": [
            {
                "user_id": u["user_id"],
                "email": u["email"],
                "first_name": u["first_name"],
                "last_name": u["last_name"],
                "company": u["company"],
                "employee_id": u["employee_id"],
                "department": u["department"],
                "status": u["status"],
                "created_at": u["created_at"],
                "approved_at": u.get("approved_at"),
                "is_admin": bool(u["is_admin"])
            }
            for u in users
        ]
    }


@router.post("/users/approve")
async def approve_user(request: ApproveUserRequest):
    """Approve a pending user"""
    success = db.approve_user(request.user_id, request.admin_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "message": "User approved successfully"
    }


@router.post("/users/reject")
async def reject_user(request: RejectUserRequest):
    """Reject a pending user"""
    success = db.reject_user(request.user_id, request.admin_id, request.reason)
    
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "message": "User rejected successfully"
    }


@router.get("/sessions/active")
async def get_active_sessions():
    """Get all active login sessions"""
    sessions = db.get_active_sessions()
    return {
        "success": True,
        "count": len(sessions),
        "sessions": [
            {
                "session_id": s["session_id"],
                "user_id": s["user_id"],
                "email": s["email"],
                "first_name": s["first_name"],
                "last_name": s["last_name"],
                "company": s["company"],
                "login_time": s["login_time"],
                "ip_address": s["ip_address"]
            }
            for s in sessions
        ]
    }


@router.get("/sessions/all")
async def get_all_sessions(limit: int = 50):
    """Get all login sessions (active and past)"""
    sessions = db.get_all_sessions(limit)
    return {
        "success": True,
        "count": len(sessions),
        "sessions": [
            {
                "session_id": s["session_id"],
                "user_id": s["user_id"],
                "email": s["email"],
                "first_name": s["first_name"],
                "last_name": s["last_name"],
                "company": s["company"],
                "employee_id": s.get("employee_id"),
                "department": s.get("department"),
                "login_time": s["login_time"],
                "logout_time": s.get("logout_time"),
                "ip_address": s["ip_address"]
            }
            for s in sessions
        ]
    }


@router.get("/activity")
async def get_admin_activity(limit: int = 50):
    """Get recent admin activity"""
    activity = db.get_admin_activity(limit)
    return {
        "success": True,
        "count": len(activity),
        "activity": [
            {
                "activity_id": a["activity_id"],
                "admin_name": f"{a['first_name']} {a['last_name']}",
                "admin_email": a["email"],
                "action": a["action"],
                "target_user_id": a.get("target_user_id"),
                "details": a.get("details"),
                "timestamp": a["timestamp"]
            }
            for a in activity
        ]
    }


@router.get("/stats")
async def get_admin_stats():
    """Get system statistics"""
    stats = db.get_stats()
    return {
        "success": True,
        "stats": stats
    }
