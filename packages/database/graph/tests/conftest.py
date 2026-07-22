"""
Pytest configuration for Neo4j tests
"""

import pytest
from neo4j import GraphDatabase
import os


@pytest.fixture(scope="function")
def neo4j_driver():
    """Create Neo4j driver for testing"""
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "aegis_dev_password")
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    yield driver
    
    # Clean up test data
    with driver.session() as session:
        session.run("MATCH (n) WHERE n.id STARTS WITH 'test-' DETACH DELETE n")
    
    driver.close()
