"""
Neo4j graph database configuration
"""

import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()


class Neo4jConfig:
    """Neo4j configuration"""
    
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "aegis_dev_password")
    
    @classmethod
    def get_driver(cls):
        """Get Neo4j driver"""
        return GraphDatabase.driver(
            cls.NEO4J_URI,
            auth=(cls.NEO4J_USER, cls.NEO4J_PASSWORD)
        )


# Global driver instance
_driver = None


def get_driver():
    """Get Neo4j driver (singleton)"""
    global _driver
    if _driver is None:
        _driver = Neo4jConfig.get_driver()
    return _driver


def close_driver():
    """Close Neo4j driver"""
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None
