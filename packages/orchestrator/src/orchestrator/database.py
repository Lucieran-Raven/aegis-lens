"""
Database Integration for Orchestrator

This module provides database integration for PostgreSQL and Neo4j
for storing verdicts, recommendations, and session data.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from contextlib import asynccontextmanager

import asyncpg
from neo4j import AsyncGraphDatabase


class PostgreSQLManager:
    """
    PostgreSQL manager for orchestrator data persistence.

    Stores verdicts, recommendations, and session metadata in PostgreSQL.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "aegis",
        user: str = "aegis_user",
        password: str = "aegis_password",
    ):
        """
        Initialize PostgreSQL manager.

        Args:
            host: PostgreSQL host
            port: PostgreSQL port
            database: Database name
            user: Database user
            password: Database password
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

        self._pool: Optional[asyncpg.Pool] = None
        self.logger = logging.getLogger(__name__)

    async def connect(self) -> None:
        """Establish PostgreSQL connection pool"""
        try:
            self._pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                min_size=2,
                max_size=10,
            )

            # Test connection
            async with self._pool.acquire() as conn:
                await conn.fetchval("SELECT 1")

            self.logger.info(f"Connected to PostgreSQL at {self.host}:{self.port}/{self.database}")

        except Exception as e:
            self.logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

    async def disconnect(self) -> None:
        """Close PostgreSQL connection pool"""
        if self._pool:
            await self._pool.close()
            self._pool = None
            self.logger.info("Disconnected from PostgreSQL")

    @property
    def pool(self) -> asyncpg.Pool:
        """Get connection pool (raises error if not connected)"""
        if self._pool is None:
            raise RuntimeError("PostgreSQL pool not connected. Call connect() first.")
        return self._pool

    @asynccontextmanager
    async def get_connection(self):
        """Context manager for PostgreSQL connection"""
        async with self.pool.acquire() as conn:
            yield conn

    async def initialize_tables(self) -> None:
        """Initialize database tables"""
        async with self.get_connection() as conn:
            # Sessions table
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    session_id VARCHAR(255) UNIQUE NOT NULL,
                    candidate_id VARCHAR(255),
                    interviewer_id VARCHAR(255),
                    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    ended_at TIMESTAMP WITH TIME ZONE,
                    status VARCHAR(50) DEFAULT 'active'
                )
            """
            )

            # Verdicts table
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS verdicts (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    session_id VARCHAR(255) NOT NULL REFERENCES sessions(session_id),
                    status VARCHAR(50) NOT NULL,
                    trust_score FLOAT NOT NULL,
                    confidence FLOAT NOT NULL,
                    reasoning TEXT,
                    anomaly JSONB,
                    trend JSONB,
                    metadata JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    INDEX idx_session_id (session_id)
                )
            """
            )

            # Recommendations table
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS recommendations (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    session_id VARCHAR(255) NOT NULL REFERENCES sessions(session_id),
                    verdict_id UUID REFERENCES verdicts(id),
                    risk_level VARCHAR(50),
                    summary TEXT,
                    recommendations JSONB,
                    suggested_flow JSONB,
                    metadata JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    INDEX idx_session_id (session_id)
                )
            """
            )

            # Trust history table
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS trust_history (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    session_id VARCHAR(255) NOT NULL REFERENCES sessions(session_id),
                    trust_score FLOAT NOT NULL,
                    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    INDEX idx_session_id (session_id),
                    INDEX idx_recorded_at (recorded_at)
                )
            """
            )

            self.logger.info("Database tables initialized")

    async def create_session(
        self,
        session_id: str,
        candidate_id: Optional[str] = None,
        interviewer_id: Optional[str] = None,
    ) -> str:
        """
        Create a new session.

        Args:
            session_id: Session identifier
            candidate_id: Candidate identifier
            interviewer_id: Interviewer identifier

        Returns:
            Session UUID
        """
        async with self.get_connection() as conn:
            result = await conn.fetchrow(
                """
                INSERT INTO sessions (session_id, candidate_id, interviewer_id)
                VALUES ($1, $2, $3)
                ON CONFLICT (session_id) DO UPDATE
                SET candidate_id = $2, interviewer_id = $3
                RETURNING id
                """,
                session_id,
                candidate_id,
                interviewer_id,
            )
            return str(result["id"])

    async def store_verdict(
        self,
        session_id: str,
        verdict: Dict[str, Any],
    ) -> str:
        """
        Store a verdict for a session.

        Args:
            session_id: Session identifier
            verdict: Verdict data dictionary

        Returns:
            Verdict UUID
        """
        async with self.get_connection() as conn:
            result = await conn.fetchrow(
                """
                INSERT INTO verdicts (
                    session_id, status, trust_score, confidence,
                    reasoning, anomaly, trend, metadata
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
                """,
                session_id,
                verdict.get("status"),
                verdict.get("trust_score"),
                verdict.get("confidence"),
                verdict.get("reasoning"),
                verdict.get("anomaly"),
                verdict.get("trend"),
                verdict.get("metadata"),
            )
            return str(result["id"])

    async def store_recommendation(
        self,
        session_id: str,
        verdict_id: str,
        recommendation: Dict[str, Any],
    ) -> str:
        """
        Store recommendations for a session.

        Args:
            session_id: Session identifier
            verdict_id: Verdict UUID
            recommendation: Recommendation data dictionary

        Returns:
            Recommendation UUID
        """
        async with self.get_connection() as conn:
            result = await conn.fetchrow(
                """
                INSERT INTO recommendations (
                    session_id, verdict_id, risk_level, summary,
                    recommendations, suggested_flow, metadata
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
                """,
                session_id,
                verdict_id,
                recommendation.get("risk_level"),
                recommendation.get("summary"),
                recommendation.get("recommendations"),
                recommendation.get("suggested_interview_flow"),
                recommendation.get("metadata"),
            )
            return str(result["id"])

    async def store_trust_score(
        self,
        session_id: str,
        trust_score: float,
    ) -> None:
        """
        Store trust score in history.

        Args:
            session_id: Session identifier
            trust_score: Trust score value
        """
        async with self.get_connection() as conn:
            await conn.execute(
                """
                INSERT INTO trust_history (session_id, trust_score)
                VALUES ($1, $2)
                """,
                session_id,
                trust_score,
            )

    async def get_session_verdicts(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get verdicts for a session.

        Args:
            session_id: Session identifier
            limit: Maximum number of verdicts

        Returns:
            List of verdict dictionaries
        """
        async with self.get_connection() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM verdicts
                WHERE session_id = $1
                ORDER BY created_at DESC
                LIMIT $2
                """,
                session_id,
                limit,
            )
            return [dict(row) for row in rows]

    async def get_trust_history(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get trust score history for a session.

        Args:
            session_id: Session identifier
            limit: Maximum number of entries

        Returns:
            List of trust score entries
        """
        async with self.get_connection() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM trust_history
                WHERE session_id = $1
                ORDER BY recorded_at DESC
                LIMIT $2
                """,
                session_id,
                limit,
            )
            return [dict(row) for row in rows]

    async def end_session(self, session_id: str) -> None:
        """
        Mark a session as ended.

        Args:
            session_id: Session identifier
        """
        async with self.get_connection() as conn:
            await conn.execute(
                """
                UPDATE sessions
                SET ended_at = NOW(), status = 'ended'
                WHERE session_id = $1
                """,
                session_id,
            )

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()


class Neo4jManager:
    """
    Neo4j manager for graph-based data storage.

    Stores relationships between sessions, candidates, and verdicts.
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "neo4j_password",
    ):
        """
        Initialize Neo4j manager.

        Args:
            uri: Neo4j connection URI
            user: Neo4j user
            password: Neo4j password
        """
        self.uri = uri
        self.user = user
        self.password = password

        self._driver: Optional[AsyncGraphDatabase.driver] = None
        self.logger = logging.getLogger(__name__)

    async def connect(self) -> None:
        """Establish Neo4j connection"""
        try:
            self._driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))

            # Test connection
            async with self._driver.session() as session:
                await session.run("RETURN 1")

            self.logger.info(f"Connected to Neo4j at {self.uri}")

        except Exception as e:
            self.logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    async def disconnect(self) -> None:
        """Close Neo4j connection"""
        if self._driver:
            await self._driver.close()
            self._driver = None
            self.logger.info("Disconnected from Neo4j")

    @property
    def driver(self) -> AsyncGraphDatabase.driver:
        """Get Neo4j driver (raises error if not connected)"""
        if self._driver is None:
            raise RuntimeError("Neo4j driver not connected. Call connect() first.")
        return self._driver

    @asynccontextmanager
    async def get_session(self):
        """Context manager for Neo4j session"""
        async with self.driver.session() as session:
            yield session

    async def initialize_constraints(self) -> None:
        """Initialize Neo4j constraints"""
        async with self.get_session() as session:
            # Create uniqueness constraints
            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Session) REQUIRE s.session_id IS UNIQUE"
            )
            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Candidate) REQUIRE c.candidate_id IS UNIQUE"
            )
            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (i:Interviewer) REQUIRE i.interviewer_id IS UNIQUE"
            )

            self.logger.info("Neo4j constraints initialized")

    async def create_session_node(
        self,
        session_id: str,
        candidate_id: Optional[str] = None,
        interviewer_id: Optional[str] = None,
    ) -> None:
        """
        Create session node and relationships.

        Args:
            session_id: Session identifier
            candidate_id: Candidate identifier
            interviewer_id: Interviewer identifier
        """
        async with self.get_session() as session:
            # Create session node
            await session.run(
                """
                MERGE (s:Session {session_id: $session_id})
                SET s.started_at = datetime()
                """,
                session_id=session_id,
            )

            # Create candidate node and relationship
            if candidate_id:
                await session.run(
                    """
                    MERGE (c:Candidate {candidate_id: $candidate_id})
                    MERGE (s:Session {session_id: $session_id})
                    MERGE (c)-[:PARTICIPATED_IN]->(s)
                    """,
                    candidate_id=candidate_id,
                    session_id=session_id,
                )

            # Create interviewer node and relationship
            if interviewer_id:
                await session.run(
                    """
                    MERGE (i:Interviewer {interviewer_id: $interviewer_id})
                    MERGE (s:Session {session_id: $session_id})
                    MERGE (i)-[:CONDUCTED]->(s)
                    """,
                    interviewer_id=interviewer_id,
                    session_id=session_id,
                )

    async def add_verdict_to_session(
        self,
        session_id: str,
        verdict: Dict[str, Any],
    ) -> None:
        """
        Add verdict to session node.

        Args:
            session_id: Session identifier
            verdict: Verdict data
        """
        async with self.get_session() as session:
            await session.run(
                """
                MATCH (s:Session {session_id: $session_id})
                CREATE (v:Verdict {
                    status: $status,
                    trust_score: $trust_score,
                    confidence: $confidence,
                    created_at: datetime()
                })
                MERGE (s)-[:HAS_VERDICT]->(v)
                """,
                session_id=session_id,
                status=verdict.get("status"),
                trust_score=verdict.get("trust_score"),
                confidence=verdict.get("confidence"),
            )

    async def add_trust_score_to_session(
        self,
        session_id: str,
        trust_score: float,
    ) -> None:
        """
        Add trust score to session node.

        Args:
            session_id: Session identifier
            trust_score: Trust score value
        """
        async with self.get_session() as session:
            await session.run(
                """
                MATCH (s:Session {session_id: $session_id})
                CREATE (t:TrustScore {
                    score: $trust_score,
                    recorded_at: datetime()
                })
                MERGE (s)-[:HAS_TRUST_SCORE]->(t)
                """,
                session_id=session_id,
                trust_score=trust_score,
            )

    async def get_candidate_sessions(
        self, candidate_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get all sessions for a candidate.

        Args:
            candidate_id: Candidate identifier
            limit: Maximum number of sessions

        Returns:
            List of session data
        """
        async with self.get_session() as session:
            result = await session.run(
                """
                MATCH (c:Candidate {candidate_id: $candidate_id})-[:PARTICIPATED_IN]->(s:Session)
                OPTIONAL MATCH (s)-[:HAS_VERDICT]->(v:Verdict)
                RETURN s, v
                ORDER BY s.started_at DESC
                LIMIT $limit
                """,
                candidate_id=candidate_id,
                limit=limit,
            )

            sessions = []
            async for record in result:
                session_data = dict(record["s"])
                verdict_data = dict(record["v"]) if record["v"] else None
                sessions.append({"session": session_data, "verdict": verdict_data})
            return sessions

    async def get_interviewer_sessions(
        self, interviewer_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get all sessions for an interviewer.

        Args:
            interviewer_id: Interviewer identifier
            limit: Maximum number of sessions

        Returns:
            List of session data
        """
        async with self.get_session() as session:
            result = await session.run(
                """
                MATCH (i:Interviewer {interviewer_id: $interviewer_id})-[:CONDUCTED]->(s:Session)
                OPTIONAL MATCH (s)-[:HAS_VERDICT]->(v:Verdict)
                RETURN s, v
                ORDER BY s.started_at DESC
                LIMIT $limit
                """,
                interviewer_id=interviewer_id,
                limit=limit,
            )

            sessions = []
            async for record in result:
                session_data = dict(record["s"])
                verdict_data = dict(record["v"]) if record["v"] else None
                sessions.append({"session": session_data, "verdict": verdict_data})
            return sessions

    async def get_session_trust_scores(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get trust scores for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of trust score data
        """
        async with self.get_session() as session:
            result = await session.run(
                """
                MATCH (s:Session {session_id: $session_id})-[:HAS_TRUST_SCORE]->(t:TrustScore)
                RETURN t
                ORDER BY t.recorded_at DESC
                """,
                session_id=session_id,
            )

            scores = []
            async for record in result:
                scores.append(dict(record["t"]))
            return scores

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()


class DatabaseManager:
    """
    Combined database manager for PostgreSQL and Neo4j.

    Provides a unified interface for both databases.
    """

    def __init__(
        self,
        postgres_config: Optional[Dict[str, Any]] = None,
        neo4j_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize combined database manager.

        Args:
            postgres_config: PostgreSQL configuration
            neo4j_config: Neo4j configuration
        """
        postgres_config = postgres_config or {}
        neo4j_config = neo4j_config or {}

        self.postgres = PostgreSQLManager(**postgres_config)
        self.neo4j = Neo4jManager(**neo4j_config)
        self.logger = logging.getLogger(__name__)

    async def connect(self) -> None:
        """Connect to both databases"""
        await self.postgres.connect()
        await self.neo4j.connect()
        self.logger.info("Connected to both databases")

    async def disconnect(self) -> None:
        """Disconnect from both databases"""
        await self.postgres.disconnect()
        await self.neo4j.disconnect()
        self.logger.info("Disconnected from both databases")

    async def initialize(self) -> None:
        """Initialize both databases"""
        await self.postgres.initialize_tables()
        await self.neo4j.initialize_constraints()
        self.logger.info("Both databases initialized")

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
