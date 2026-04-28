from neo4j import GraphDatabase, AsyncGraphDatabase
from typing import Optional
from app.core.config import settings


class Neo4jConnection:
    """Neo4j connection manager."""
    
    def __init__(self):
        self.driver = None
    
    async def connect(self):
        """Establish connection to Neo4j."""
        self.driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
    
    async def disconnect(self):
        """Close Neo4j connection."""
        if self.driver:
            await self.driver.close()
    
    async def initialize_schema(self):
        """Initialize graph schema with constraints and indexes."""
        async with self.driver.session() as session:
            # Node types: Document, Framework, Concept, Technology, Impact, Citation
            
            # Uniqueness constraints
            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE"
            )
            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (f:Framework) REQUIRE f.id IS UNIQUE"
            )
            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE"
            )
            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Technology) REQUIRE t.id IS UNIQUE"
            )
            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (i:Impact) REQUIRE i.id IS UNIQUE"
            )
            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (ct:Citation) REQUIRE ct.id IS UNIQUE"
            )
            
            # Existence constraints
            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Document) REQUIRE d.title IS NOT NULL"
            )
            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (f:Framework) REQUIRE f.name IS NOT NULL"
            )
            
            # Composite indexes for query optimization
            await session.run(
                "CREATE INDEX IF NOT EXISTS FOR (d:Document) ON (d.tenant_id, d.created_at)"
            )
            await session.run(
                "CREATE INDEX IF NOT EXISTS FOR (f:Framework) ON (f.tenant_id, f.category)"
            )
            await session.run(
                "CREATE INDEX IF NOT EXISTS FOR (c:Concept) ON (c.tenant_id, c.type)"
            )


neo4j_connection = Neo4jConnection()
