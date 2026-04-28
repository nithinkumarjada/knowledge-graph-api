import hashlib
import uuid
from typing import Dict, List, Any
from datetime import datetime
from neo4j import AsyncGraphDatabase
from app.core.config import settings


class IngestionService:
    """Idempotent document ingestion pipeline."""
    
    def __init__(self):
        self.driver = None
    
    async def connect(self):
        """Connect to Neo4j."""
        self.driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
    
    async def disconnect(self):
        """Disconnect from Neo4j."""
        if self.driver:
            await self.driver.close()
    
    @staticmethod
    def _generate_idempotent_id(content: str, source: str) -> str:
        """Generate deterministic ID based on content hash."""
        combined = f"{content}:{source}"
        return hashlib.sha256(combined.encode()).hexdigest()[:12]
    
    async def ingest_document(
        self, 
        title: str, 
        content: str, 
        source: str,
        tenant_id: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Ingest document with idempotency - deduplication by content hash."""
        doc_id = self._generate_idempotent_id(content, source)
        
        async with self.driver.session() as session:
            # Check if document already exists (idempotent)
            result = await session.run(
                """
                MATCH (d:Document {id: $doc_id, tenant_id: $tenant_id})
                RETURN d.id
                """,
                doc_id=doc_id,
                tenant_id=tenant_id
            )
            
            existing = await result.single()
            if existing:
                return doc_id
            
            # Create document node
            await session.run(
                """
                CREATE (d:Document {
                    id: $doc_id,
                    tenant_id: $tenant_id,
                    title: $title,
                    content: $content,
                    source: $source,
                    created_at: datetime(),
                    metadata: $metadata
                })
                """,
                doc_id=doc_id,
                tenant_id=tenant_id,
                title=title,
                content=content,
                source=source,
                metadata=metadata or {}
            )
            
            # Extract and create citations
            citations = await self._extract_citations(content, doc_id, tenant_id)
            await self._create_citations(doc_id, citations, tenant_id)
        
        return doc_id
    
    async def _extract_citations(
        self, 
        content: str, 
        doc_id: str,
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """Extract citations from document content."""
        # Simple extraction: look for references like [ref:xyz] or [cite:xyz]
        citations = []
        
        import re
        pattern = r'\[(?:ref|cite):([^\]]+)\]'
        matches = re.findall(pattern, content)
        
        for match in matches:
            citations.append({
                "reference_id": match,
                "confidence_score": 0.9
            })
        
        return citations
    
    async def _create_citations(
        self, 
        doc_id: str, 
        citations: List[Dict[str, Any]],
        tenant_id: str
    ):
        """Create citation relationships, deduplicating by (source, target)."""
        async with self.driver.session() as session:
            for citation in citations:
                citation_id = f"{doc_id}:{citation['reference_id']}"
                
                # Check if citation already exists
                result = await session.run(
                    """
                    MATCH (c:Citation {id: $citation_id, tenant_id: $tenant_id})
                    RETURN c.id
                    """,
                    citation_id=citation_id,
                    tenant_id=tenant_id
                )
                
                existing = await result.single()
                if existing:
                    continue
                
                # Create citation node
                await session.run(
                    """
                    CREATE (c:Citation {
                        id: $citation_id,
                        tenant_id: $tenant_id,
                        source_id: $source_id,
                        target_id: $target_id,
                        confidence_score: $confidence_score,
                        created_at: datetime()
                    })
                    """,
                    citation_id=citation_id,
                    tenant_id=tenant_id,
                    source_id=doc_id,
                    target_id=citation["reference_id"],
                    confidence_score=citation["confidence_score"]
                )
    
    async def ingest_framework_catalog(
        self,
        frameworks: List[Dict[str, Any]],
        tenant_id: str
    ) -> List[str]:
        """Ingest framework catalog with idempotency."""
        framework_ids = []
        
        async with self.driver.session() as session:
            for framework in frameworks:
                framework_id = framework.get("id", str(uuid.uuid4()))
                
                # Check if framework exists
                result = await session.run(
                    """
                    MATCH (f:Framework {id: $framework_id, tenant_id: $tenant_id})
                    RETURN f.id
                    """,
                    framework_id=framework_id,
                    tenant_id=tenant_id
                )
                
                existing = await result.single()
                if existing:
                    framework_ids.append(framework_id)
                    continue
                
                # Create framework node
                await session.run(
                    """
                    CREATE (f:Framework {
                        id: $framework_id,
                        tenant_id: $tenant_id,
                        name: $name,
                        category: $category,
                        description: $description,
                        version: $version,
                        created_at: datetime()
                    })
                    """,
                    framework_id=framework_id,
                    tenant_id=tenant_id,
                    name=framework.get("name"),
                    category=framework.get("category"),
                    description=framework.get("description"),
                    version=framework.get("version", "1.0")
                )
                
                framework_ids.append(framework_id)
        
        return framework_ids
