from typing import List, Dict, Any
from neo4j import AsyncGraphDatabase
from app.core.config import settings


class QueryService:
    """Cypher query library for graph analysis."""
    
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
    
    async def forward_traceability(
        self, 
        source_id: str, 
        tenant_id: str,
        max_depth: int = 5
    ) -> Dict[str, Any]:
        """Find all downstream dependencies (forward traceability)."""
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH path = (start {id: $source_id, tenant_id: $tenant_id})-[*1..%d]->(target)
                WHERE all(node IN nodes(path) WHERE node.tenant_id = $tenant_id)
                RETURN {
                    source: start.id,
                    targets: collect(distinct target.id),
                    paths: collect({
                        nodes: [n.id for n in nodes(path)],
                        relationships: [type(r) for r in relationships(path)]
                    })
                } as result
                """ % max_depth,
                source_id=source_id,
                tenant_id=tenant_id
            )
            
            record = await result.single()
            return record["result"] if record else {}
    
    async def backward_traceability(
        self, 
        target_id: str, 
        tenant_id: str,
        max_depth: int = 5
    ) -> Dict[str, Any]:
        """Find all upstream dependencies (backward traceability)."""
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH path = (source)-[*1..%d]->(end {id: $target_id, tenant_id: $tenant_id})
                WHERE all(node IN nodes(path) WHERE node.tenant_id = $tenant_id)
                RETURN {
                    target: end.id,
                    sources: collect(distinct source.id),
                    paths: collect({
                        nodes: [n.id for n in nodes(path)],
                        relationships: [type(r) for r in relationships(path)]
                    })
                } as result
                """ % max_depth,
                target_id=target_id,
                tenant_id=tenant_id
            )
            
            record = await result.single()
            return record["result"] if record else {}
    
    async def framework_coverage(
        self, 
        framework_id: str, 
        tenant_id: str
    ) -> Dict[str, Any]:
        """Analyze framework coverage against requirements/concepts."""
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (f:Framework {id: $framework_id, tenant_id: $tenant_id})
                OPTIONAL MATCH (f)-[r:COVERS|IMPLEMENTS]->(c:Concept)
                WHERE c.tenant_id = $tenant_id
                WITH f, collect({id: c.id, name: c.name, type: c.type}) as covered_concepts
                
                OPTIONAL MATCH (all_concepts:Concept {tenant_id: $tenant_id})
                WITH f, covered_concepts, collect(all_concepts.id) as all_concept_ids
                
                RETURN {
                    framework_id: f.id,
                    framework_name: f.name,
                    covered_concepts: covered_concepts,
                    total_concepts: size(all_concept_ids),
                    coverage_percentage: (toFloat(size(covered_concepts)) / toFloat(size(all_concept_ids))) * 100,
                    uncovered_concepts: [c IN all_concept_ids WHERE NOT c IN [x.id FOR x IN covered_concepts]]
                } as result
                """,
                framework_id=framework_id,
                tenant_id=tenant_id
            )
            
            record = await result.single()
            return record["result"] if record else {}
    
    async def gap_detection(
        self, 
        framework_id: str, 
        tenant_id: str
    ) -> Dict[str, Any]:
        """Detect gaps between framework and requirements."""
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (f:Framework {id: $framework_id, tenant_id: $tenant_id})
                
                // Get all concepts required but not covered
                MATCH (req:Concept {tenant_id: $tenant_id})
                WHERE NOT (f)-[:COVERS|IMPLEMENTS]->(req)
                
                WITH f, collect({id: req.id, name: req.name, type: req.type}) as gap_concepts
                
                // Get related technologies that might fill gaps
                OPTIONAL MATCH (gap:Concept)-[:RELATED_TO|REQUIRES]->(tech:Technology)
                WHERE gap IN gap_concepts AND tech.tenant_id = $tenant_id
                WITH f, gap_concepts, collect(distinct {id: tech.id, name: tech.name}) as related_technologies
                
                RETURN {
                    framework_id: f.id,
                    framework_name: f.name,
                    gap_count: size(gap_concepts),
                    gaps: gap_concepts,
                    suggested_technologies: related_technologies
                } as result
                """,
                framework_id=framework_id,
                tenant_id=tenant_id
            )
            
            record = await result.single()
            return record["result"] if record else {}
    
    async def impact_analysis(
        self, 
        node_id: str, 
        node_type: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Analyze impact of changes on a specific node."""
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (node:%(node_type)s {id: $node_id, tenant_id: $tenant_id})
                
                // Find all downstream impacts
                OPTIONAL MATCH path = (node)-[r:DEPENDS_ON|IMPLEMENTS|REQUIRES|RELATED_TO*1..5]->(impacted)
                WHERE all(n IN nodes(path) WHERE n.tenant_id = $tenant_id)
                WITH node, collect(distinct {id: impacted.id, labels: labels(impacted)}) as impacted_nodes
                
                // Calculate impact score based on relationship depth
                OPTIONAL MATCH (node)-[]->(depth1)
                OPTIONAL MATCH (depth1)-[]->(depth2)
                OPTIONAL MATCH (depth2)-[]->(depth3)
                
                RETURN {
                    node_id: node.id,
                    node_type: labels(node)[0],
                    impacted_nodes: impacted_nodes,
                    impact_score: (size(impacted_nodes) * 0.3),
                    affected_frameworks: []
                } as result
                """ % {"node_type": node_type},
                node_id=node_id,
                tenant_id=tenant_id
            )
            
            record = await result.single()
            return record["result"] if record else {}
