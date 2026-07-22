"""
Neo4j Cypher queries for knowledge graph operations
"""

from typing import List, Dict, Optional, Any
from .config import get_driver


class GraphQueries:
    """Neo4j graph database queries"""
    
    def __init__(self):
        self.driver = get_driver()
    
    def create_candidate(self, candidate_id: str, email_hash: str, position_applied: str, status: str) -> Dict[str, Any]:
        """Create a candidate node"""
        with self.driver.session() as session:
            query = """
            MERGE (c:Candidate {id: $id})
            SET c.email_hash = $email_hash,
                c.position_applied = $position_applied,
                c.status = $status,
                c.created_at = datetime()
            RETURN c
            """
            result = session.run(
                query,
                id=candidate_id,
                email_hash=email_hash,
                position_applied=position_applied,
                status=status
            )
            return result.single()[0]
    
    def create_claim(self, claim_id: str, candidate_id: str, text: str, claim_type: str, 
                     confidence: float, session_id: str) -> Dict[str, Any]:
        """Create a claim node and connect to candidate"""
        with self.driver.session() as session:
            query = """
            MATCH (c:Candidate {id: $candidate_id})
            CREATE (cl:Claim {
                id: $id,
                text: $text,
                type: $type,
                confidence: $confidence,
                session_id: $session_id,
                created_at: datetime()
            })
            CREATE (c)-[:HAS_CLAIM {timestamp: datetime()}]->(cl)
            RETURN cl
            """
            result = session.run(
                query,
                id=claim_id,
                candidate_id=candidate_id,
                text=text,
                type=claim_type,
                confidence=confidence,
                session_id=session_id
            )
            return result.single()[0]
    
    def create_entity(self, entity_id: str, name: str, entity_type: str, source: str) -> Dict[str, Any]:
        """Create an entity node"""
        with self.driver.session() as session:
            query = """
            MERGE (e:Entity {id: $id})
            SET e.name = $name,
                e.type = $type,
                e.source = $source,
                e.created_at = datetime()
            RETURN e
            """
            result = session.run(
                query,
                id=entity_id,
                name=name,
                type=entity_type,
                source=source
            )
            return result.single()[0]
    
    def link_claim_to_entity(self, claim_id: str, entity_id: str, confidence: float) -> bool:
        """Link a claim to an entity"""
        with self.driver.session() as session:
            query = """
            MATCH (cl:Claim {id: $claim_id})
            MATCH (e:Entity {id: $entity_id})
            MERGE (cl)-[:MENTIONED_IN {confidence: $confidence}]->(e)
            RETURN true
            """
            result = session.run(
                query,
                claim_id=claim_id,
                entity_id=entity_id,
                confidence=confidence
            )
            return result.single()[0]
    
    def find_contradictions(self, candidate_id: str, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Find contradictory claims for a candidate"""
        with self.driver.session() as session:
            query = """
            MATCH (c:Candidate {id: $candidate_id})-[:HAS_CLAIM]->(cl1:Claim)
            MATCH (c)-[:HAS_CLAIM]->(cl2:Claim)
            WHERE cl1.id < cl2.id
            AND cl1.type = cl2.type
            AND cl1.confidence > $threshold
            AND cl2.confidence > $threshold
            WITH cl1, cl2, 
                 apoc.text.levenshteinSimilarity(cl1.text, cl2.text) as similarity
            WHERE similarity < 0.5
            RETURN cl1.id as claim1_id, cl1.text as claim1_text,
                   cl2.id as claim2_id, cl2.text as claim2_text,
                   similarity
            ORDER BY similarity ASC
            LIMIT 10
            """
            result = session.run(query, candidate_id=candidate_id, threshold=threshold)
            return [record.data() for record in result]
    
    def get_candidate_knowledge_graph(self, candidate_id: str) -> Dict[str, Any]:
        """Get the complete knowledge graph for a candidate"""
        with self.driver.session() as session:
            query = """
            MATCH (c:Candidate {id: $candidate_id})
            OPTIONAL MATCH (c)-[:HAS_CLAIM]->(cl:Claim)
            WITH c, collect(DISTINCT properties(cl)) as claims
            OPTIONAL MATCH (c)-[:HAS_CLAIM]->(cl2:Claim)-[:MENTIONED_IN]->(e:Entity)
            WITH c, claims, collect(DISTINCT properties(e)) as entities
            OPTIONAL MATCH (c)-[:HAS_SKILL]->(s:Skill)
            WITH c, claims, entities, collect(DISTINCT properties(s)) as skills
            OPTIONAL MATCH (c)-[:WORKED_AT]->(co:Company)
            WITH c, claims, entities, skills, collect(DISTINCT properties(co)) as companies
            OPTIONAL MATCH (c)-[:EDUCATED_AT]->(i:Institution)
            WITH c, claims, entities, skills, companies, collect(DISTINCT properties(i)) as institutions
            RETURN {
                candidate: properties(c),
                claims: claims,
                entities: entities,
                skills: skills,
                companies: companies,
                institutions: institutions
            } as graph
            """
            result = session.run(query, candidate_id=candidate_id)
            return result.single()[0]
    
    def find_related_entities(self, entity_id: str, max_depth: int = 2) -> List[Dict[str, Any]]:
        """Find entities related to a given entity"""
        with self.driver.session() as session:
            query = """
            MATCH (e:Entity {id: $entity_id})
            CALL apoc.path.subgraphAll(e, {
                maxLevel: $max_depth,
                relationshipFilter: "MENTIONED_IN|RELATED_TO|WORKED_AT|EDUCATED_AT"
            })
            YIELD nodes, relationships
            RETURN nodes, relationships
            """
            result = session.run(query, entity_id=entity_id, max_depth=max_depth)
            return [record.data() for record in result]
    
    def verify_claim(self, claim_id: str, source: str, confidence: float, verified: bool) -> bool:
        """Mark a claim as verified or disputed"""
        with self.driver.session() as session:
            rel_type = "VERIFIED_BY" if verified else "DISPUTED_BY"
            query = f"""
            MATCH (cl:Claim {{id: $claim_id}})
            MERGE (cl)-[:{rel_type} {{
                source: $source,
                confidence: $confidence,
                verified_at: datetime()
            }}]->(:VerificationSource {{name: $source}})
            RETURN true
            """
            result = session.run(
                query,
                claim_id=claim_id,
                source=source,
                confidence=confidence
            )
            return result.single()[0]
