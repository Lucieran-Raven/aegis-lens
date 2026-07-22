"""
Neo4j knowledge graph schema definitions
"""

# Node labels
NODE_LABELS = {
    "Candidate": "Candidate in the system",
    "Entity": "Named entity (person, company, etc.)",
    "Claim": "Claim or statement made by candidate",
    "Skill": "Technical or professional skill",
    "Project": "Project or work experience",
    "Education": "Educational background",
    "Certification": "Professional certification",
    "Company": "Company or organization",
    "Institution": "Educational institution",
}

# Relationship types
RELATIONSHIP_TYPES = {
    "HAS_CLAIM": "Candidate made a claim",
    "HAS_SKILL": "Candidate has a skill",
    "WORKED_AT": "Candidate worked at a company",
    "PROJECT_AT": "Candidate worked on a project at a company",
    "EDUCATED_AT": "Candidate educated at an institution",
    "HAS_CERTIFICATION": "Candidate has a certification",
    "MENTIONED_IN": "Entity mentioned in a claim",
    "CONTRADICTS": "Claim contradicts another claim",
    "SUPPORTS": "Claim supports another claim",
    "RELATED_TO": "Entity is related to another entity",
    "VERIFIED_BY": "Claim verified by external source",
    "DISPUTED_BY": "Claim disputed by external source",
}

# Node properties
NODE_PROPERTIES = {
    "Candidate": {
        "id": "string (unique identifier)",
        "email_hash": "string (SHA-256 hash)",
        "position_applied": "string",
        "status": "string",
    },
    "Entity": {
        "id": "string (unique identifier)",
        "name": "string",
        "type": "string (person, company, institution)",
        "source": "string (where entity was extracted)",
    },
    "Claim": {
        "id": "string (unique identifier)",
        "text": "string (claim text)",
        "type": "string (employment, education, skill)",
        "confidence": "float (0-1)",
        "session_id": "string (reference to session)",
    },
    "Skill": {
        "id": "string (unique identifier)",
        "name": "string",
        "category": "string (technical, soft, domain)",
        "proficiency": "string (beginner, intermediate, expert)",
    },
    "Project": {
        "id": "string (unique identifier)",
        "name": "string",
        "description": "string",
        "start_date": "date",
        "end_date": "date",
    },
    "Education": {
        "id": "string (unique identifier)",
        "degree": "string",
        "field": "string",
        "start_date": "date",
        "end_date": "date",
    },
    "Certification": {
        "id": "string (unique identifier)",
        "name": "string",
        "issuer": "string",
        "issue_date": "date",
        "expiry_date": "date",
    },
    "Company": {
        "id": "string (unique identifier)",
        "name": "string",
        "industry": "string",
        "website": "string",
    },
    "Institution": {
        "id": "string (unique identifier)",
        "name": "string",
        "type": "string (university, college, bootcamp)",
        "location": "string",
    },
}

# Relationship properties
RELATIONSHIP_PROPERTIES = {
    "HAS_CLAIM": {
        "timestamp": "datetime",
        "context": "string (where claim was made)",
    },
    "HAS_SKILL": {
        "proficiency": "string",
        "verified": "boolean",
        "verified_at": "datetime",
    },
    "WORKED_AT": {
        "start_date": "date",
        "end_date": "date",
        "position": "string",
        "verified": "boolean",
    },
    "PROJECT_AT": {
        "role": "string",
        "verified": "boolean",
    },
    "EDUCATED_AT": {
        "start_date": "date",
        "end_date": "date",
        "degree": "string",
        "verified": "boolean",
    },
    "HAS_CERTIFICATION": {
        "issue_date": "date",
        "expiry_date": "date",
        "verified": "boolean",
    },
    "MENTIONED_IN": {
        "confidence": "float",
    },
    "CONTRADICTS": {
        "confidence": "float",
        "evidence": "string",
    },
    "SUPPORTS": {
        "confidence": "float",
        "evidence": "string",
    },
    "RELATED_TO": {
        "relationship_type": "string",
        "confidence": "float",
    },
    "VERIFIED_BY": {
        "source": "string",
        "confidence": "float",
        "verified_at": "datetime",
    },
    "DISPUTED_BY": {
        "source": "string",
        "confidence": "float",
        "disputed_at": "datetime",
    },
}


# Schema constraints and indexes
CONSTRAINTS = [
    # Unique constraints
    "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Candidate) REQUIRE c.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (cl:Claim) REQUIRE cl.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Skill) REQUIRE s.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (ed:Education) REQUIRE ed.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Certification) REQUIRE c.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (co:Company) REQUIRE co.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (i:Institution) REQUIRE i.id IS UNIQUE",
]

INDEXES = [
    # Lookup indexes
    "CREATE INDEX IF NOT EXISTS FOR (c:Candidate) ON (c.email_hash)",
    "CREATE INDEX IF NOT EXISTS FOR (cl:Claim) ON (cl.session_id)",
    "CREATE INDEX IF NOT EXISTS FOR (e:Entity) ON (e.name)",
    "CREATE INDEX IF NOT EXISTS FOR (e:Entity) ON (e.type)",
    "CREATE INDEX IF NOT EXISTS FOR (s:Skill) ON (s.name)",
    "CREATE INDEX IF NOT EXISTS FOR (s:Skill) ON (s.category)",
    "CREATE INDEX IF NOT EXISTS FOR (co:Company) ON (co.name)",
    "CREATE INDEX IF NOT EXISTS FOR (i:Institution) ON (i.name)",
]


def initialize_schema(driver):
    """Initialize Neo4j schema with constraints and indexes"""
    with driver.session() as session:
        # Create constraints
        for constraint in CONSTRAINTS:
            try:
                session.run(constraint)
            except Exception as e:
                print(f"Warning creating constraint: {e}")
        
        # Create indexes
        for index in INDEXES:
            try:
                session.run(index)
            except Exception as e:
                print(f"Warning creating index: {e}")
