from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.models import (
    TraceabilityPath, 
    GapAnalysis, 
    ImpactAnalysis,
    TokenData
)
from app.core.security import verify_token
from app.services.query import QueryService
from app.services.audit import AuditService
from app.db.postgres import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/queries", tags=["queries"])
query_service = QueryService()


@router.get("/forward-traceability/{source_id}")
async def get_forward_traceability(
    source_id: str,
    max_depth: int = 5,
    token_data: TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
) -> dict:
    """Get forward traceability (downstream dependencies)."""
    try:
        await query_service.connect()
        
        result = await query_service.forward_traceability(
            source_id=source_id,
            tenant_id=token_data.tenant_id,
            max_depth=max_depth
        )
        
        AuditService.log_action(
            db=db,
            tenant_id=token_data.tenant_id,
            user_id=token_data.user_id,
            action="FORWARD_TRACEABILITY_QUERY",
            resource_type="Query",
            resource_id=source_id
        )
        
        return result
    
    finally:
        await query_service.disconnect()


@router.get("/backward-traceability/{target_id}")
async def get_backward_traceability(
    target_id: str,
    max_depth: int = 5,
    token_data: TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
) -> dict:
    """Get backward traceability (upstream dependencies)."""
    try:
        await query_service.connect()
        
        result = await query_service.backward_traceability(
            target_id=target_id,
            tenant_id=token_data.tenant_id,
            max_depth=max_depth
        )
        
        AuditService.log_action(
            db=db,
            tenant_id=token_data.tenant_id,
            user_id=token_data.user_id,
            action="BACKWARD_TRACEABILITY_QUERY",
            resource_type="Query",
            resource_id=target_id
        )
        
        return result
    
    finally:
        await query_service.disconnect()


@router.get("/framework-coverage/{framework_id}")
async def get_framework_coverage(
    framework_id: str,
    token_data: TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
) -> dict:
    """Analyze framework coverage against concepts."""
    try:
        await query_service.connect()
        
        result = await query_service.framework_coverage(
            framework_id=framework_id,
            tenant_id=token_data.tenant_id
        )
        
        AuditService.log_action(
            db=db,
            tenant_id=token_data.tenant_id,
            user_id=token_data.user_id,
            action="FRAMEWORK_COVERAGE_QUERY",
            resource_type="Query",
            resource_id=framework_id
        )
        
        return result
    
    finally:
        await query_service.disconnect()


@router.get("/gap-detection/{framework_id}")
async def get_gap_detection(
    framework_id: str,
    token_data: TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
) -> dict:
    """Detect gaps between framework and requirements."""
    try:
        await query_service.connect()
        
        result = await query_service.gap_detection(
            framework_id=framework_id,
            tenant_id=token_data.tenant_id
        )
        
        AuditService.log_action(
            db=db,
            tenant_id=token_data.tenant_id,
            user_id=token_data.user_id,
            action="GAP_DETECTION_QUERY",
            resource_type="Query",
            resource_id=framework_id
        )
        
        return result
    
    finally:
        await query_service.disconnect()


@router.get("/impact-analysis/{node_id}")
async def get_impact_analysis(
    node_id: str,
    node_type: str = "Document",
    token_data: TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
) -> dict:
    """Analyze impact of changes on a specific node."""
    try:
        await query_service.connect()
        
        result = await query_service.impact_analysis(
            node_id=node_id,
            node_type=node_type,
            tenant_id=token_data.tenant_id
        )
        
        AuditService.log_action(
            db=db,
            tenant_id=token_data.tenant_id,
            user_id=token_data.user_id,
            action="IMPACT_ANALYSIS_QUERY",
            resource_type="Query",
            resource_id=node_id
        )
        
        return result
    
    finally:
        await query_service.disconnect()
