from fastapi import APIRouter, Depends
from typing import List
from app.schemas.models import TokenData
from app.core.security import verify_token
from app.services.audit import AuditService
from app.db.postgres import get_db, AuditLog
from sqlalchemy.orm import Session

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/logs")
async def get_audit_logs(
    limit: int = 100,
    token_data: TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
) -> List[dict]:
    """Get audit logs for the tenant."""
    logs = AuditService.get_audit_logs(
        db=db,
        tenant_id=token_data.tenant_id,
        limit=limit
    )
    
    return [
        {
            "id": log.id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "user_id": log.user_id,
            "timestamp": log.timestamp.isoformat(),
            "details": log.details
        }
        for log in logs
    ]


@router.get("/logs/{user_id}")
async def get_user_audit_logs(
    user_id: str,
    limit: int = 100,
    token_data: TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
) -> List[dict]:
    """Get audit logs for a specific user (multi-tenancy scoped)."""
    logs = AuditService.get_audit_logs(
        db=db,
        tenant_id=token_data.tenant_id,
        user_id=user_id,
        limit=limit
    )
    
    return [
        {
            "id": log.id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "user_id": log.user_id,
            "timestamp": log.timestamp.isoformat(),
            "details": log.details
        }
        for log in logs
    ]
