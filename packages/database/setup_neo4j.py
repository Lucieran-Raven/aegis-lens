"""Neo4j production setup and schema initialization script"""

import os
import sys
import logging
from typing import Optional, Dict, Any

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jSetup:
    """Production Neo4j setup and schema initialization manager"""
    
    def __init__(self, uri: str, user: str, password: str):
        """Initialize Neo4j setup"""
        self.uri = uri
        self.user = user
        self.password = password
        self.driver: Optional[GraphDatabase.driver] = None
    
    def connect(self) -> None:
        """Connect to Neo4j server"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # Verify connection
            self.driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {self.uri}")
        except (ServiceUnavailable, AuthError) as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            self.driver = None
            logger.info("Neo4j connection closed")
    
    def create_constraints(self) -> None:
        """Create uniqueness constraints for nodes"""
        constraints = [
            "CREATE CONSTRAINT candidate_id_unique IF NOT EXISTS FOR (c:Candidate) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT session_id_unique IF NOT EXISTS FOR (s:Session) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT company_name_unique IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE",
            "CREATE CONSTRAINT skill_name_unique IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE",
            "CREATE CONSTRAINT job_id_unique IF NOT EXISTS FOR (j:Job) REQUIRE j.id IS UNIQUE",
        ]
        
        try:
            self.connect()
            with self.driver.session() as session:
                for constraint in constraints:
                    try:
                        session.run(constraint)
                        logger.info(f"Constraint created: {constraint}")
                    except Exception as e:
                        logger.warning(f"Constraint may already exist: {e}")
        except Exception as e:
            logger.error(f"Failed to create constraints: {e}")
            raise
        finally:
            self.disconnect()
    
    def create_indexes(self) -> None:
        """Create indexes for frequently queried properties"""
        indexes = [
            "CREATE INDEX candidate_email_index IF NOT EXISTS FOR (c:Candidate) ON (c.email)",
            "CREATE INDEX candidate_name_index IF NOT EXISTS FOR (c:Candidate) ON (c.name)",
            "CREATE INDEX session_created_at_index IF NOT EXISTS FOR (s:Session) ON (s.created_at)",
            "CREATE INDEX job_title_index IF NOT EXISTS FOR (j:Job) ON (j.title)",
            "CREATE INDEX skill_category_index IF NOT EXISTS FOR (s:Skill) ON (s.category)",
        ]
        
        try:
            self.connect()
            with self.driver.session() as session:
                for index in indexes:
                    try:
                        session.run(index)
                        logger.info(f"Index created: {index}")
                    except Exception as e:
                        logger.warning(f"Index may already exist: {e}")
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise
        finally:
            self.disconnect()
    
    def initialize_schema(self) -> None:
        """Initialize graph schema with sample data structure"""
        try:
            self.connect()
            with self.driver.session() as session:
                # Create sample nodes to verify schema
                session.run("""
                    MERGE (s:Skill {name: 'Python', category: 'Programming'})
                    MERGE (s2:Skill {name: 'JavaScript', category: 'Programming'})
                    MERGE (s3:Skill {name: 'Machine Learning', category: 'AI/ML'})
                """)
                logger.info("Sample schema data initialized")
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            raise
        finally:
            self.disconnect()
    
    def verify_setup(self) -> bool:
        """Verify Neo4j setup is working"""
        try:
            self.connect()
            with self.driver.session() as session:
                # Check database version
                result = session.run("CALL dbms.components() YIELD name, versions, edition RETURN name, versions[0] as version, edition")
                for record in result:
                    logger.info(f"Neo4j {record['name']} {record['version']} ({record['edition']})")
                
                # Check constraints
                result = session.run("SHOW CONSTRAINTS")
                constraints = list(result)
                logger.info(f"Constraints: {len(constraints)}")
                
                # Check indexes
                result = session.run("SHOW INDEXES")
                indexes = list(result)
                logger.info(f"Indexes: {len(indexes)}")
                
                # Check node counts
                result = session.run("MATCH (n) RETURN labels(n) as label, count(*) as count")
                for record in result:
                    logger.info(f"Nodes {record['label']}: {record['count']}")
                
                return True
        except Exception as e:
            logger.error(f"Setup verification failed: {e}")
            return False
        finally:
            self.disconnect()
    
    def clear_database(self) -> None:
        """Clear all data from database (use with caution)"""
        try:
            self.connect()
            with self.driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
                logger.warning("Database cleared")
        except Exception as e:
            logger.error(f"Failed to clear database: {e}")
            raise
        finally:
            self.disconnect()


def main():
    """Main setup function"""
    # Get configuration from environment
    uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    user = os.getenv('NEO4J_USER', 'neo4j')
    password = os.getenv('NEO4J_PASSWORD', 'aegis_dev_password')
    
    logger.info("Starting Neo4j production setup...")
    
    setup = Neo4jSetup(uri, user, password)
    
    try:
        # Step 1: Create constraints
        setup.create_constraints()
        
        # Step 2: Create indexes
        setup.create_indexes()
        
        # Step 3: Initialize schema
        setup.initialize_schema()
        
        # Step 4: Verify setup
        if setup.verify_setup():
            logger.info("Neo4j setup completed successfully!")
            return 0
        else:
            logger.error("Neo4j setup verification failed")
            return 1
            
    except Exception as e:
        logger.error(f"Neo4j setup failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
