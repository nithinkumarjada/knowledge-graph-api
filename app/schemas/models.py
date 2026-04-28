from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


# Document Schemas
class DocumentBase(BaseModel):
    title: str
    content: str
    source: str
    metadata: Optional[Dict[str, Any]] = None


class DocumentCreate(DocumentBase):
    pass


class Document(DocumentBase):
    id: str
    tenant_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Framework Schemas
class FrameworkBase(BaseModel):
    name: str
    category: str
    description: str
    version: str


class FrameworkCreate(FrameworkBase):
    pass


class Framework(FrameworkBase):
    id: str
    tenant_id: str
    
    class Config:
        from_attributes = True


# Concept Schemas
class ConceptBase(BaseModel):
    name: str
    type: str
    description: Optional[str] = None


class ConceptCreate(ConceptBase):
    pass


class Concept(ConceptBase):
    id: str
    tenant_id: str
    
    class Config:
        from_attributes = True


# Technology Schemas
class TechnologyBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None


class TechnologyCreate(TechnologyBase):
    pass


class Technology(TechnologyBase):
    id: str
    tenant_id: str
    
    class Config:
        from_attributes = True


# Citation Schemas
class CitationBase(BaseModel):
    source_document_id: str
    target_node_id: str
    target_node_type: str
    confidence_score: float


class CitationCreate(CitationBase):
    pass


class Citation(CitationBase):
    id: str
    tenant_id: str
    
    class Config:
        from_attributes = True


# Query Response Schemas
class TraceabilityPath(BaseModel):
    path: List[Dict[str, Any]]
    length: int


class GapAnalysis(BaseModel):
    gaps: List[str]
    coverage_percentage: float


class ImpactAnalysis(BaseModel):
    impacted_nodes: List[str]
    impact_score: float
    affected_frameworks: List[str]


# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    tenant_id: str
    user_id: str
