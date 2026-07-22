"""
Tests for Neo4j graph schema
"""

import pytest
from graph.schema import initialize_schema, NODE_LABELS, RELATIONSHIP_TYPES


def test_schema_initialization(neo4j_driver):
    """Test schema initialization with constraints and indexes"""
    # This should not raise any errors
    initialize_schema(neo4j_driver)
    assert True


def test_node_labels_defined():
    """Test that all node labels are defined"""
    assert "Candidate" in NODE_LABELS
    assert "Entity" in NODE_LABELS
    assert "Claim" in NODE_LABELS
    assert "Skill" in NODE_LABELS
    assert len(NODE_LABELS) == 9


def test_relationship_types_defined():
    """Test that all relationship types are defined"""
    assert "HAS_CLAIM" in RELATIONSHIP_TYPES
    assert "HAS_SKILL" in RELATIONSHIP_TYPES
    assert "WORKED_AT" in RELATIONSHIP_TYPES
    assert "CONTRADICTS" in RELATIONSHIP_TYPES
    assert len(RELATIONSHIP_TYPES) == 12
