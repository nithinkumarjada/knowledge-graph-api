from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.postgres import AuditLog


class AuditService:
    """PostgreSQL audit logging service."""
    
    @staticmethod
    def log_action(
        db: Session,
        tenant_id: str,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: Optional[str] = None
    ) -> AuditLog:
        """Create an audit log entry."""
        audit_log = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            timestamp=datetime.utcnow()
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return audit_log
    
    @staticmethod
    def get_audit_logs(
        db: Session,
        tenant_id: str,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> list[AuditLog]:
        """Retrieve audit logs with optional filtering."""
        query = db.query(AuditLog).filter(AuditLog.tenant_id == tenant_id)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
