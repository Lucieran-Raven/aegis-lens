# AEGIS LENS - WebSocket Protocol

## Overview

The WebSocket protocol enables real-time bidirectional communication between the client and server for live interview sessions, agent updates, and metric streaming.

## Connection

### WebSocket URL

```
ws://localhost:8000/ws
```

### Authentication

WebSocket connections require authentication via query parameter:

```
ws://localhost:8000/ws?token=<jwt_token>
```

## Message Format

All messages follow this structure:

```json
{
  "type": "message_type",
  "data": {},
  "timestamp": "2024-01-01T00:00:00Z",
  "message_id": "uuid"
}
```

## Message Types

### Client → Server

#### 1. Join Session

```json
{
  "type": "join_session",
  "data": {
    "session_id": "uuid",
    "user_type": "candidate|interviewer|observer"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "message_id": "uuid"
}
```

**Response:**
```json
{
  "type": "session_joined",
  "data": {
    "session_id": "uuid",
    "status": "in_progress",
    "participants": ["user_id_1", "user_id_2"]
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "message_id": "uuid"
}
```

#### 2. Start Agent Analysis

```json
{
  "type": "start_agent",
  "data": {
    "session_id": "uuid",
    "agent_name": "chronos",
    "agent_type": "physics"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "message_id": "uuid"
}
```

#### 3. Stop Agent Analysis

```json
{
  "type": "stop_agent",
  "data": {
    "session_id": "uuid",
    "agent_name": "chronos"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "message_id": "uuid"
}
```

#### 4. Send Metric Data

```json
{
  "type": "metric_data",
  "data": {
    "session_id": "uuid",
    "agent_name": "chronos",
    "metrics": {
      "jitter": 15.2,
      "timestamp": "2024-01-01T00:00:00Z"
    }
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "message_id": "uuid"
}
```

#### 5. Heartbeat

```json
{
  "type": "heartbeat",
  "data": {},
  "timestamp": "2024-01-01T00:00:00Z",
  "message_id": "uuid"
}
```

### Server → Client

#### 1. Agent Result Update

```json
{
  "type": "agent_result",
  "data": {
    "session_id": "uuid",
    "agent_name": "chronos",
    "agent_type": "physics",
    "score": 0.85,
    "confidence": 0.92,
    "status": "clear",
    "metrics": {
      "mean_jitter": 15.2,
      "std_jitter": 2.8
    }
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "message_id": "uuid"
}
```

#### 2. Metric Stream

```json
{
  "type": "metric_stream",
  "data": {
    "session_id": "uuid",
    "agent_name": "chronos",
    "metrics": {
      "jitter": 14.8,
      "timestamp": "2024-01-01T00:00:01Z"
    }
  },
  "timestamp": "2024-01-01T00:00:01Z",
  "message_id": "uuid"
}
```

#### 3. Session Status Update

```json
{
  "type": "session_status",
  "data": {
    "session_id": "uuid",
    "status": "in_progress",
    "duration_seconds": 300
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "message_id": "uuid"
}
```

#### 4. Alert Notification

```json
{
  "type": "alert",
  "data": {
    "session_id": "uuid",
    "alert_type": "anomaly_detected",
    "severity": "high",
    "message": "Unusual jitter pattern detected",
    "agent_name": "chronos"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "message_id": "uuid"
}
```

#### 5. Intelligence Update

```json
{
  "type": "intelligence_update",
  "data": {
    "candidate_id": "uuid",
    "source": "linkedin",
    "intel_type": "employment",
    "confidence": 0.95,
    "is_verified": true
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "message_id": "uuid"
}
```

#### 6. Knowledge Graph Update

```json
{
  "type": "graph_update",
  "data": {
    "candidate_id": "uuid",
    "update_type": "claim_added",
    "claim": {
      "id": "uuid",
      "text": "I worked at Google",
      "type": "employment"
    }
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "message_id": "uuid"
}
```

#### 7. Heartbeat Response

```json
{
  "type": "heartbeat_ack",
  "data": {},
  "timestamp": "2024-01-01T00:00:00Z",
  "message_id": "uuid"
}
```

#### 8. Error

```json
{
  "type": "error",
  "data": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": {}
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "message_id": "uuid"
}
```

## Connection Lifecycle

### 1. Connection Established

```json
{
  "type": "connected",
  "data": {
    "connection_id": "uuid",
    "server_time": "2024-01-01T00:00:00Z"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "message_id": "uuid"
}
```

### 2. Authentication

Client sends token, server validates:

```json
{
  "type": "authenticated",
  "data": {
    "user_id": "uuid",
    "permissions": ["read", "write"]
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "message_id": "uuid"
}
```

### 3. Session Join

Client joins a session, server confirms:

```json
{
  "type": "session_joined",
  "data": {
    "session_id": "uuid",
    "status": "in_progress"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "message_id": "uuid"
}
```

### 4. Active Session

Server streams real-time updates:

- Agent results
- Metric data
- Alerts
- Status updates

### 5. Session Leave

```json
{
  "type": "leave_session",
  "data": {
    "session_id": "uuid"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "message_id": "uuid"
}
```

### 6. Disconnection

```json
{
  "type": "disconnected",
  "data": {
    "reason": "client_initiated|server_initiated|timeout"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "message_id": "uuid"
}
```

## Heartbeat

- Client sends heartbeat every 30 seconds
- Server responds with heartbeat_ack
- If no heartbeat for 60 seconds, server closes connection

```json
{
  "type": "heartbeat",
  "data": {},
  "timestamp": "2024-01-01T00:00:00Z",
  "message_id": "uuid"
}
```

## Error Handling

### Authentication Error

```json
{
  "type": "error",
  "data": {
    "code": "AUTH_001",
    "message": "Invalid authentication token"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "message_id": "uuid"
}
```

### Session Not Found

```json
{
  "type": "error",
  "data": {
    "code": "SESSION_001",
    "message": "Session not found"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "message_id": "uuid"
}
```

### Agent Error

```json
{
  "type": "error",
  "data": {
    "code": "AGENT_001",
    "message": "Agent failed to start",
    "agent_name": "chronos"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "message_id": "uuid"
}
```

## Rate Limiting

- Max 100 messages per second per connection
- Burst up to 200 messages for 5 seconds
- Exceeding limits results in warning then disconnection

## Reconnection Strategy

1. Exponential backoff: 1s, 2s, 4s, 8s, 16s, 32s
2. Max retry attempts: 10
3. After successful reconnection, rejoin sessions
4. Request missed updates since disconnect

## Security

- All connections must be authenticated
- TLS/WSS required in production
- Token validation on every message
- Rate limiting per connection
- IP-based blocking for abuse

## Compression

- Message compression enabled for payloads > 1KB
- Using per-message deflate compression
- Client can negotiate compression level

## Binary Data Support

For high-frequency metric streaming, binary format available:

```
Binary format: [type(1 byte)][session_id(16 bytes)][timestamp(8 bytes)][data...]
```

## Example Session Flow

```
Client → Server: connect with token
Server → Client: connected
Client → Server: join_session
Server → Client: session_joined
Client → Server: start_agent (chronos)
Server → Client: agent_started
Server → Client: metric_stream (continuous)
Server → Client: agent_result (periodic)
Server → Client: alert (if anomaly)
Client → Server: stop_agent
Server → Client: agent_stopped
Client → Server: leave_session
Server → Client: session_left
Client → Server: disconnect
```
