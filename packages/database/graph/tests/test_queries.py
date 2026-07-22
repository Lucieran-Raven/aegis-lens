"""
Tests for Neo4j graph queries
"""

import pytest
from graph.queries import GraphQueries


def test_create_candidate(neo4j_driver):
    """Test creating a candidate node"""
    queries = GraphQueries()
    queries.driver = neo4j_driver
    
    candidate = queries.create_candidate(
        candidate_id="test-candidate-1",
        email_hash="abc123",
        position_applied="Software Engineer",
        status="pending"
    )
    
    assert candidate["id"] == "test-candidate-1"
    assert candidate["email_hash"] == "abc123"
    assert candidate["position_applied"] == "Software Engineer"


def test_create_claim(neo4j_driver):
    """Test creating a claim node"""
    queries = GraphQueries()
    queries.driver = neo4j_driver
    
    # First create a candidate
    queries.create_candidate(
        candidate_id="test-candidate-2",
        email_hash="xyz789",
        position_applied="Data Scientist",
        status="active"
    )
    
    # Then create a claim
    claim = queries.create_claim(
        claim_id="test-claim-1",
        candidate_id="test-candidate-2",
        text="I worked at Google for 5 years",
        claim_type="employment",
        confidence=0.9,
        session_id="test-session-1"
    )
    
    assert claim["id"] == "test-claim-1"
    assert claim["text"] == "I worked at Google for 5 years"
    assert claim["type"] == "employment"


def test_create_entity(neo4j_driver):
    """Test creating an entity node"""
    queries = GraphQueries()
    queries.driver = neo4j_driver
    
    entity = queries.create_entity(
        entity_id="test-entity-1",
        name="Google",
        entity_type="company",
        source="linkedin"
    )
    
    assert entity["id"] == "test-entity-1"
    assert entity["name"] == "Google"
    assert entity["type"] == "company"


def test_link_claim_to_entity(neo4j_driver):
    """Test linking a claim to an entity"""
    queries = GraphQueries()
    queries.driver = neo4j_driver
    
    # Create candidate
    queries.create_candidate(
        candidate_id="test-candidate-3",
        email_hash="def456",
        position_applied="Backend Engineer",
        status="active"
    )
    
    # Create claim
    queries.create_claim(
        claim_id="test-claim-2",
        candidate_id="test-candidate-3",
        text="I worked at Amazon",
        claim_type="employment",
        confidence=0.85,
        session_id="test-session-2"
    )
    
    # Create entity
    queries.create_entity(
        entity_id="test-entity-2",
        name="Amazon",
        entity_type="company",
        source="resume"
    )
    
    # Link claim to entity
    result = queries.link_claim_to_entity(
        claim_id="test-claim-2",
        entity_id="test-entity-2",
        confidence=0.9
    )
    
    assert result is True


def test_get_candidate_knowledge_graph(neo4j_driver):
    """Test retrieving candidate knowledge graph"""
    queries = GraphQueries()
    queries.driver = neo4j_driver
    
    # Create candidate with data
    queries.create_candidate(
        candidate_id="test-candidate-4",
        email_hash="ghi789",
        position_applied="Full Stack Developer",
        status="active"
    )
    
    queries.create_claim(
        claim_id="test-claim-3",
        candidate_id="test-candidate-4",
        text="I know Python and JavaScript",
        claim_type="skill",
        confidence=0.95,
        session_id="test-session-3"
    )
    
    # Get knowledge graph
    graph = queries.get_candidate_knowledge_graph("test-candidate-4")
    
    assert "candidate" in graph
    assert "claims" in graph
    assert graph["candidate"]["id"] == "test-candidate-4"
