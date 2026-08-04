# JWT Authentication Policy

## Overview
This document outlines the JWT (JSON Web Token) authentication implementation for the Aegis-Lens platform. JWTs are used for secure, stateless authentication across all services.

## JWT Structure

### Token Format
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### Header
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Payload
```json
{
  "sub": "user-id",
  "name": "user-name",
  "role": "user-role",
  "iat": 1516239022,
  "exp": 1516242622,
  "jti": "unique-token-id"
}
```

## Implementation

### Token Generation
```typescript
import jwt from 'jsonwebtoken';

class JwtService {
  private secret: string;
  private expiresIn: string;
  private refreshExpiresIn: string;

  constructor() {
    this.secret = process.env.JWT_SECRET || 'your-secret-key';
    this.expiresIn = process.env.JWT_EXPIRATION || '24h';
    this.refreshExpiresIn = process.env.JWT_REFRESH_EXPIRATION || '7d';
  }

  generateAccessToken(userId: string, role: string): string {
    const payload = {
      sub: userId,
      role: role,
      type: 'access',
      iat: Math.floor(Date.now() / 1000),
      jti: this.generateJti()
    };

    return jwt.sign(payload, this.secret, {
      expiresIn: this.expiresIn,
      algorithm: 'HS256'
    });
  }

  generateRefreshToken(userId: string): string {
    const payload = {
      sub: userId,
      type: 'refresh',
      iat: Math.floor(Date.now() / 1000),
      jti: this.generateJti()
    };

    return jwt.sign(payload, this.secret, {
      expiresIn: this.refreshExpiresIn,
      algorithm: 'HS256'
    });
  }

  private generateJti(): string {
    return crypto.randomUUID();
  }

  verifyToken(token: string): any {
    try {
      return jwt.verify(token, this.secret, {
        algorithms: ['HS256']
      });
    } catch (error) {
      throw new Error('Invalid token');
    }
  }

  decodeToken(token: string): any {
    return jwt.decode(token, { complete: true });
  }
}
```

### Token Validation Middleware
```typescript
import { Request, Response, NextFunction } from 'express';

class AuthMiddleware {
  private jwtService: JwtService;

  constructor() {
    this.jwtService = new JwtService();
  }

  authenticate(req: Request, res: Response, next: NextFunction): void {
    const token = this.extractToken(req);

    if (!token) {
      return res.status(401).json({ error: 'No token provided' });
    }

    try {
      const decoded = this.jwtService.verifyToken(token);

      if (decoded.type !== 'access') {
        return res.status(401).json({ error: 'Invalid token type' });
      }

      req.user = {
        id: decoded.sub,
        role: decoded.role,
        jti: decoded.jti
      };

      next();
    } catch (error) {
      return res.status(401).json({ error: 'Invalid token' });
    }
  }

  authorize(roles: string[]) {
    return (req: Request, res: Response, next: NextFunction) => {
      if (!req.user) {
        return res.status(401).json({ error: 'Unauthorized' });
      }

      if (!roles.includes(req.user.role)) {
        return res.status(403).json({ error: 'Forbidden' });
      }

      next();
    };
  }

  private extractToken(req: Request): string | null {
    const authHeader = req.headers.authorization;

    if (authHeader && authHeader.startsWith('Bearer ')) {
      return authHeader.substring(7);
    }

    return null;
  }
}
```

### Token Refresh
```typescript
class RefreshTokenService {
  private jwtService: JwtService;
  private redis: Redis;

  constructor() {
    this.jwtService = new JwtService();
    this.redis = new Redis(process.env.REDIS_URL);
  }

  async refreshAccessToken(refreshToken: string): Promise<string> {
    try {
      const decoded = this.jwtService.verifyToken(refreshToken);

      if (decoded.type !== 'refresh') {
        throw new Error('Invalid token type');
      }

      // Check if refresh token is revoked
      const isRevoked = await this.redis.get(`revoked:${decoded.jti}`);
      if (isRevoked) {
        throw new Error('Token revoked');
      }

      // Generate new access token
      const user = await this.getUserById(decoded.sub);
      return this.jwtService.generateAccessToken(user.id, user.role);
    } catch (error) {
      throw new Error('Invalid refresh token');
    }
  }

  async revokeToken(jti: string): Promise<void> {
    await this.redis.setex(`revoked:${jti}`, 604800, '1'); // 7 days
  }
}
```

## Security Best Practices

### Token Storage
- **Access Tokens**: Store in memory or httpOnly cookies
- **Refresh Tokens**: Store in httpOnly, secure, sameSite cookies
- **Never**: Store tokens in localStorage or sessionStorage

### Token Expiration
- **Access Tokens**: 15 minutes to 1 hour
- **Refresh Tokens**: 7 days to 30 days
- Implement token rotation on refresh

### Token Revocation
- Maintain token blacklist in Redis
- Revoke tokens on logout
- Revoke tokens on password change
- Revoke tokens on role change

### Secret Management
- Use strong, random secrets (minimum 32 bytes)
- Rotate secrets regularly (every 90 days)
- Store secrets in Kubernetes Secrets
- Never commit secrets to version control

## Claims

### Standard Claims
- **sub**: Subject (user ID)
- **iat**: Issued at (timestamp)
- **exp**: Expiration time (timestamp)
- **jti**: JWT ID (unique identifier)
- **iss**: Issuer (service identifier)
- **aud**: Audience (intended recipient)

### Custom Claims
- **role**: User role for authorization
- **permissions**: Array of user permissions
- **type**: Token type (access/refresh)
- **session_id**: Session identifier

## Token Lifecycle

### Login Flow
1. User authenticates with credentials
2. Server validates credentials
3. Server generates access and refresh tokens
4. Server stores refresh token in database/Redis
5. Server returns tokens to client

### Access Flow
1. Client includes access token in request header
2. Middleware validates token
3. Middleware extracts user information
4. Request proceeds to handler

### Refresh Flow
1. Client sends refresh token
2. Server validates refresh token
3. Server checks if token is revoked
4. Server generates new access token
5. Server returns new access token

### Logout Flow
1. Client sends logout request
2. Server revokes refresh token
3. Server adds access token JTI to blacklist
4. Client deletes tokens

## Monitoring

### Metrics
- Token generation rate
- Token validation success/failure rate
- Token refresh rate
- Token revocation rate
- Average token lifetime

### Alerting
- High token failure rate
- Suspicious token patterns
- Brute force attempts
- Token expiration anomalies

## Compliance

### Regulatory Requirements
- **GDPR**: Secure authentication mechanisms
- **HIPAA**: Access control and authentication
- **SOC 2**: Access control monitoring
- **PCI DSS**: Strong authentication controls

### Audit Logging
- Log all token generation events
- Log all token validation failures
- Log all token revocations
- Maintain logs for minimum 90 days

## Testing

### Unit Tests
- Token generation
- Token validation
- Token expiration
- Token revocation

### Integration Tests
- Authentication flow
- Authorization flow
- Token refresh flow
- Logout flow

### Security Tests
- Secret strength validation
- Token tampering detection
- Replay attack prevention
- Timing attack resistance

## Contact

For questions about JWT authentication:
- Security Team: security@aegis-lens.local
- Development Team: dev@aegis-lens.local
