# AEGIS LENS - API Design

## Overview

The AEGIS LENS API provides RESTful endpoints for managing candidates, sessions, agent results, intelligence data, and knowledge graph operations. The API is built with FastAPI and follows OpenAPI 3.0 specification.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All endpoints require Bearer token authentication:

```
Authorization: Bearer <token>
```

## Response Format

All responses follow this structure:

```json
{
  "success": true,
  "data": {},
  "message": "Operation successful",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

Error responses:

```json
{
  "sucess": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": {}
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Endpoints

### Candidates

#### Create Candidate

```http
POST /api/v1/candidates
```

**Request Body:**
```json
{
  "email_hash": "sha256_hash_of_email",
  "position_applied": "Software Engineer",
  "resume_hash": "sha256_hash_of_resume",
  "linkedin_hash": "sha256_hash_of_linkedin",
  "github_hash": "sha256_hash_of_github"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email_hash": "sha256_hash",
    "position_applied": "Software Engineer",
    "status": "pending",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

#### Get Candidate

```http
GET /api/v1/candidates/{candidate_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email_hash": "sha256_hash",
    "position_applied": "Software Engineer",
    "status": "active",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

#### List Candidates

```http
GET /api/v1/candidates?status=active&limit=50&offset=0
```

**Response:**
```json
{
  "success": true,
  "data": {
    "candidates": [],
    "total": 100,
    "limit": 50,
    "offset": 0
  }
}
```

#### Update Candidate Status

```http
PATCH /api/v1/candidates/{candidate_id}/status
```

**Request Body:**
```json
{
  "status": "active"
}
```

### Sessions

#### Create Session

```http
POST /api/v1/sessions
```

**Request Body:**
```json
{
  "candidate_id": "uuid",
  "interview_type": "technical",
  "interviewer_id": "uuid"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "candidate_id": "uuid",
    "started_at": "2024-01-01T00:00:00Z",
    "status": "scheduled",
    "interview_type": "technical"
  }
}
```

#### Get Session

```http
GET /api/v1/sessions/{session_id}
```

#### Update Session

```http
PATCH /api/v1/sessions/{session_id}
```

**Request Body:**
```json
{
  "status": "in_progress",
  "ended_at": "2024-01-01T01:00:00Z",
  "duration_seconds": 3600
}
```

#### End Session with Verdict

```http
POST /api/v1/sessions/{session_id}/complete
```

**Request Body:**
```json
{
  "final_verdict": "hire",
  "final_trust_score": 0.85,
  "notes": "Strong technical skills"
}
```

### Agent Results

#### Create Agent Result

```http
POST /api/v1/sessions/{session_id}/agent-results
```

**Request Body:**
```json
{
  "agent_name": "chronos",
  "agent_type": "physics",
  "score": 0.85,
  "confidence": 0.92,
  "status": "clear",
  "metrics": {
    "mean_jitter": 15.2,
    "std_jitter": 2.8
  }
}
```

#### Get Agent Results for Session

```http
GET /api/v1/sessions/{session_id}/agent-results
```

#### Get Agent Result

```http
GET /api/v1/agent-results/{result_id}
```

### Intelligence

#### Create Intelligence

```http
POST /api/v1/candidates/{candidate_id}/intelligence
```

**Request Body:**
```json
{
  "source": "linkedin",
  "intel_type": "employment",
  "data": {
    "company": "Tech Corp",
    "position": "Senior Developer",
    "start_date": "2020-01-01",
    "end_date": "2022-12-31"
  },
  "confidence": 0.95,
  "relevance": 0.9
}
```

#### Get Intelligence for Candidate

```http
GET /api/v1/candidates/{candidate_id}/intelligence
```

#### Verify Intelligence

```http
PATCH /api/v1/intelligence/{intel_id}/verify
```

**Request Body:**
```json
{
  "is_verified": true,
  "verification_method": "manual",
  "verified_at": "2024-01-01T00:00:00Z"
}
```

### Knowledge Graph

#### Get Candidate Knowledge Graph

```http
GET /api/v1/candidates/{candidate_id}/knowledge-graph
```

**Response:**
```json
{
  "success": true,
  "data": {
    "candidate": {},
    "claims": [],
    "entities": [],
    "skills": [],
    "companies": [],
    "institutions": []
  }
}
```

#### Find Contradictions

```http
GET /api/v1/candidates/{candidate_id}/contradictions?threshold=0.7
```

**Response:**
```json
{
  "success": true,
  "data": {
    "contradictions": [
      {
        "claim1_id": "uuid",
        "claim1_text": "I worked at Google",
        "claim2_id": "uuid",
        "claim2_text": "I never worked at Google",
        "similarity": 0.3
      }
    ]
  }
}
```

### Metrics (Time-Series)

#### Create Physics Metric

```http
POST /api/v1/sessions/{session_id}/metrics/physics
```

**Request Body:**
```json
{
  "agent_name": "chronos",
  "score": 0.92,
  "confidence": 0.88,
  "status": "clear",
  "metrics": {
    "mean_jitter": 14.5,
    "std_jitter": 2.3
  }
}
```

#### Get Physics Metrics for Session

```http
GET /api/v1/sessions/{session_id}/metrics/physics?start=2024-01-01T00:00:00Z&end=2024-01-01T23:59:59Z
```

#### Get Agent Metrics

```http
GET /api/v1/sessions/{session_id}/metrics/agents?start=2024-01-01T00:00:00Z&end=2024-01-01T23:59:59Z
```

#### Get System Metrics

```http
GET /api/v1/metrics/system?category=performance&start=2024-01-01T00:00:00Z&end=2024-01-01T23:59:59Z
```

### Health & Status

#### Health Check

```http
GET /api/v1/health
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "database": "connected",
    "timescale": "connected",
    "neo4j": "connected",
    "redis": "connected"
  }
}
```

#### API Status

```http
GET /api/v1/status
```

**Response:**
```json
{
  "success": true,
  "data": {
    "version": "1.0.0",
    "environment": "development",
    "uptime": 3600
  }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| AUTH_001 | Invalid or missing authentication token |
| AUTH_002 | Token expired |
| AUTH_003 | Insufficient permissions |
| VAL_001 | Validation error |
| VAL_002 | Invalid request format |
| DB_001 | Database connection error |
| DB_002 | Record not found |
| DB_003 | Duplicate record |
| GRAPH_001 | Neo4j connection error |
| GRAPH_002 | Graph query error |
| SRV_001 | Internal server error |
| SRV_002 | Service unavailable |

## Rate Limiting

- **Standard**: 100 requests per minute per IP
- **Burst**: 200 requests per minute per IP
- Headers included: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Pagination

List endpoints support pagination:

- `limit`: Number of items per page (default: 50, max: 100)
- `offset`: Number of items to skip (default: 0)

Response includes:
- `total`: Total number of items
- `limit`: Current page limit
- `offset`: Current offset

## Filtering & Sorting

List endpoints support filtering and sorting:

```
GET /api/v1/candidates?status=active&sort_by=created_at&sort_order=desc
```

## Webhooks

### Webhook Events

- `candidate.created`: New candidate created
- `session.started`: Interview session started
- `session.completed`: Interview session completed
- `agent.result`: Agent analysis result available
- `intelligence.verified`: Intelligence verified

### Webhook Configuration

```http
POST /api/v1/webhooks
```

**Request Body:**
```json
{
  "url": "https://example.com/webhook",
  "events": ["candidate.created", "session.completed"],
  "secret": "webhook_secret"
}
```

## WebSocket API

See [WebSocket Protocol Design](./WEBSOCKET_PROTOCOL.md) for real-time communication details.
