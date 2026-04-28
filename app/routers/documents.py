from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.models import Document, DocumentCreate, TokenData
from app.core.security import verify_token
from app.services.ingestion import IngestionService
from app.services.audit import AuditService
from app.db.postgres import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/documents", tags=["documents"])
ingestion_service = IngestionService()


@router.post("/ingest", response_model=dict)
async def ingest_document(
    document: DocumentCreate,
    token_data: TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
) -> dict:
    """Ingest a new document into the knowledge graph."""
    try:
        await ingestion_service.connect()
        
        doc_id = await ingestion_service.ingest_document(
            title=document.title,
            content=document.content,
            source=document.source,
            tenant_id=token_data.tenant_id,
            metadata=document.metadata
        )
        
        # Audit log
        AuditService.log_action(
            db=db,
            tenant_id=token_data.tenant_id,
            user_id=token_data.user_id,
            action="DOCUMENT_INGESTED",
            resource_type="Document",
            resource_id=doc_id,
            details=document.title
        )
        
        return {
            "id": doc_id,
            "title": document.title,
            "status": "ingested",
            "tenant_id": token_data.tenant_id
        }
    
    finally:
        await ingestion_service.disconnect()


@router.post("/ingest-batch")
async def ingest_batch(
    documents: List[DocumentCreate],
    token_data: TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
) -> dict:
    """Batch ingest multiple documents."""
    try:
        await ingestion_service.connect()
        
        doc_ids = []
        for document in documents:
            doc_id = await ingestion_service.ingest_document(
                title=document.title,
                content=document.content,
                source=document.source,
                tenant_id=token_data.tenant_id,
                metadata=document.metadata
            )
            doc_ids.append(doc_id)
            
            AuditService.log_action(
                db=db,
                tenant_id=token_data.tenant_id,
                user_id=token_data.user_id,
                action="DOCUMENT_INGESTED",
                resource_type="Document",
                resource_id=doc_id,
                details=document.title
            )
        
        return {
            "ingested_count": len(doc_ids),
            "document_ids": doc_ids,
            "tenant_id": token_data.tenant_id
        }
    
    finally:
        await ingestion_service.disconnect()
