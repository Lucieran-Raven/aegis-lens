# Access Control Policy

## Overview
This document outlines the access control implementation for the Aegis-Lens platform. Access control ensures that users and services can only access resources they are authorized to use.

## Access Control Model

### RBAC (Role-Based Access Control)
- Users are assigned roles
- Roles have permissions
- Permissions grant access to resources

### ABAC (Attribute-Based Access Control)
- Access based on user attributes
- Context-aware decisions
- Dynamic policy evaluation

## Roles and Permissions

### User Roles

#### Admin
- Full system access
- User management
- System configuration
- Audit log access

#### HR Manager
- Candidate management
- Session management
- Report generation
- Team member access

#### Recruiter
- View candidates
- Conduct sessions
- View reports
- Limited candidate editing

#### Interviewer
- View assigned candidates
- Conduct assigned sessions
- Submit feedback
- View own reports

#### Viewer
- Read-only access
- View candidates
- View reports
- No editing capabilities

### Service Roles

#### Orchestrator Service
- Session orchestration
- Agent coordination
- Resource allocation
- State management

#### Agent Service
- AI agent execution
- Model inference
- Data processing
- Result generation

#### Database Service
- Data persistence
- Query execution
- Transaction management
- Backup operations

## Implementation

### Permission System
```typescript
enum Permission {
  // Candidate permissions
  CANDIDATE_READ = 'candidate:read',
  CANDIDATE_WRITE = 'candidate:write',
  CANDIDATE_DELETE = 'candidate:delete',

  // Session permissions
  SESSION_READ = 'session:read',
  SESSION_WRITE = 'session:write',
  SESSION_DELETE = 'session:delete',
  SESSION_CONDUCT = 'session:conduct',

  // Report permissions
  REPORT_READ = 'report:read',
  REPORT_GENERATE = 'report:generate',
  REPORT_EXPORT = 'report:export',

  // User permissions
  USER_READ = 'user:read',
  USER_WRITE = 'user:write',
  USER_DELETE = 'user:delete',

  // System permissions
  SYSTEM_CONFIG = 'system:config',
  SYSTEM_AUDIT = 'system:audit',
  SYSTEM_ADMIN = 'system:admin'
}

interface Role {
  name: string;
  permissions: Permission[];
}

const ROLES: Record<string, Role> = {
  admin: {
    name: 'Admin',
    permissions: Object.values(Permission)
  },
  hr_manager: {
    name: 'HR Manager',
    permissions: [
      Permission.CANDIDATE_READ,
      Permission.CANDIDATE_WRITE,
      Permission.CANDIDATE_DELETE,
      Permission.SESSION_READ,
      Permission.SESSION_WRITE,
      Permission.SESSION_DELETE,
      Permission.REPORT_READ,
      Permission.REPORT_GENERATE,
      Permission.REPORT_EXPORT,
      Permission.USER_READ,
      Permission.USER_WRITE
    ]
  },
  recruiter: {
    name: 'Recruiter',
    permissions: [
      Permission.CANDIDATE_READ,
      Permission.CANDIDATE_WRITE,
      Permission.SESSION_READ,
      Permission.SESSION_CONDUCT,
      Permission.REPORT_READ,
      Permission.REPORT_GENERATE
    ]
  },
  interviewer: {
    name: 'Interviewer',
    permissions: [
      Permission.CANDIDATE_READ,
      Permission.SESSION_READ,
      Permission.SESSION_CONDUCT,
      Permission.REPORT_READ
    ]
  },
  viewer: {
    name: 'Viewer',
    permissions: [
      Permission.CANDIDATE_READ,
      Permission.SESSION_READ,
      Permission.REPORT_READ
    ]
  }
};
```

### Authorization Middleware
```typescript
class AuthorizationService {
  private roles: Record<string, Role>;

  constructor() {
    this.roles = ROLES;
  }

  hasPermission(userRole: string, permission: Permission): boolean {
    const role = this.roles[userRole];
    if (!role) {
      return false;
    }
    return role.permissions.includes(permission);
  }

  hasAnyPermission(userRole: string, permissions: Permission[]): boolean {
    return permissions.some(permission => 
      this.hasPermission(userRole, permission)
    );
  }

  hasAllPermissions(userRole: string, permissions: Permission[]): boolean {
    return permissions.every(permission => 
      this.hasPermission(userRole, permission)
    );
  }

  authorize(permission: Permission) {
    return (req: Request, res: Response, next: NextFunction) => {
      if (!req.user) {
        return res.status(401).json({ error: 'Unauthorized' });
      }

      if (!this.hasPermission(req.user.role, permission)) {
        return res.status(403).json({ error: 'Forbidden' });
      }

      next();
    };
  }

  authorizeAny(permissions: Permission[]) {
    return (req: Request, res: Response, next: NextFunction) => {
      if (!req.user) {
        return res.status(401).json({ error: 'Unauthorized' });
      }

      if (!this.hasAnyPermission(req.user.role, permissions)) {
        return res.status(403).json({ error: 'Forbidden' });
      }

      next();
    };
  }
}
```

### Resource-Based Access Control
```typescript
class ResourceAccessService {
  async canAccessResource(
    userId: string,
    resourceType: string,
    resourceId: string
  ): Promise<boolean> {
    // Check if user owns the resource
    const isOwner = await this.checkOwnership(userId, resourceType, resourceId);
    if (isOwner) {
      return true;
    }

    // Check if user has permission through role
    const user = await this.getUser(userId);
    const permission = this.getPermissionForResource(resourceType);
    
    return this.authorizationService.hasPermission(user.role, permission);
  }

  async checkOwnership(
    userId: string,
    resourceType: string,
    resourceId: string
  ): Promise<boolean> {
    switch (resourceType) {
      case 'candidate':
        return this.checkCandidateOwnership(userId, resourceId);
      case 'session':
        return this.checkSessionOwnership(userId, resourceId);
      case 'report':
        return this.checkReportOwnership(userId, resourceId);
      default:
        return false;
    }
  }

  private getPermissionForResource(resourceType: string): Permission {
    const permissionMap: Record<string, Permission> = {
      candidate: Permission.CANDIDATE_READ,
      session: Permission.SESSION_READ,
      report: Permission.REPORT_READ
    };
    return permissionMap[resourceType];
  }
}
```

### Service-to-Service Authentication
```typescript
class ServiceAuthMiddleware {
  private serviceTokens: Map<string, string>;

  constructor() {
    this.serviceTokens = new Map();
    this.initializeServiceTokens();
  }

  private initializeServiceTokens(): void {
    // Load service tokens from environment or secrets
    this.serviceTokens.set('orchestrator', process.env.ORCHESTRATOR_TOKEN);
    this.serviceTokens.set('agents', process.env.AGENTS_TOKEN);
    this.serviceTokens.set('database', process.env.DATABASE_TOKEN);
  }

  authenticateService(req: Request, res: Response, next: NextFunction): void {
    const serviceToken = req.headers['x-service-token'] as string;
    const serviceName = req.headers['x-service-name'] as string;

    if (!serviceToken || !serviceName) {
      return res.status(401).json({ error: 'Service authentication required' });
    }

    const expectedToken = this.serviceTokens.get(serviceName);
    if (!expectedToken || expectedToken !== serviceToken) {
      return res.status(401).json({ error: 'Invalid service token' });
    }

    req.service = { name: serviceName };
    next();
  }
}
```

## Network Access Control

### Kubernetes Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: aegis-lens-network-policy
  namespace: aegis-lens
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: aegis-lens
    ports:
    - protocol: TCP
      port: 80
    - protocol: TCP
      port: 443
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: aegis-lens
    ports:
    - protocol: TCP
      port: 53
    - protocol: TCP
      port: 443
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: TCP
      port: 53
```

### Service Mesh (Istio)
```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: aegis-lens-authz
  namespace: aegis-lens
spec:
  selector:
    matchLabels:
      app: orchestrator
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/aegis-lens/sa/agents"]
    to:
    - operation:
        methods: ["POST", "GET"]
        paths: ["/api/*"]
```

## API Access Control

### Rate Limiting
```typescript
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';

const rateLimiter = rateLimit({
  store: new RedisStore({
    client: redis,
    prefix: 'rate_limit:'
  }),
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP',
  standardHeaders: true,
  legacyHeaders: false,
});

// Role-based rate limits
const roleRateLimits: Record<string, number> = {
  admin: 1000,
  hr_manager: 500,
  recruiter: 200,
  interviewer: 100,
  viewer: 50
};

function getRateLimitForRole(role: string): number {
  return roleRateLimits[role] || 50;
}
```

### IP Whitelisting
```typescript
class IpWhitelistService {
  private whitelistedIps: Set<string>;

  constructor() {
    this.whitelistedIps = new Set();
    this.loadWhitelist();
  }

  private loadWhitelist(): void {
    const whitelist = process.env.IP_WHITELIST?.split(',') || [];
    whitelist.forEach(ip => this.whitelistedIps.add(ip.trim()));
  }

  isWhitelisted(ip: string): boolean {
    return this.whitelistedIps.has(ip);
  }

  middleware() {
    return (req: Request, res: Response, next: NextFunction) => {
      const clientIp = req.ip;
      
      if (!this.isWhitelisted(clientIp)) {
        return res.status(403).json({ error: 'IP not whitelisted' });
      }

      next();
    };
  }
}
```

## Audit Logging

### Access Events
```typescript
interface AccessEvent {
  userId: string;
  resource: string;
  action: string;
  success: boolean;
  timestamp: Date;
  ipAddress: string;
  userAgent: string;
}

class AuditLogger {
  private logAccess(event: AccessEvent): void {
    // Log to secure audit system
    console.log(JSON.stringify({
      ...event,
      timestamp: event.timestamp.toISOString()
    }));
  }

  logAccessAttempt(
    userId: string,
    resource: string,
    action: string,
    success: boolean,
    req: Request
  ): void {
    const event: AccessEvent = {
      userId,
      resource,
      action,
      success,
      timestamp: new Date(),
      ipAddress: req.ip,
      userAgent: req.headers['user-agent'] || 'unknown'
    };

    this.logAccess(event);
  }
}
```

## Compliance

### Regulatory Requirements
- **GDPR**: Article 32 - Security of processing
- **HIPAA**: 45 CFR § 164.308 - Administrative safeguards
- **SOC 2**: CC6.1 - Logical and physical access controls
- **PCI DSS**: Requirement 7 - Restrict access to system components

### Access Reviews
- Quarterly access reviews
- Role permission audits
- User access certifications
- Privileged access reviews

## Best Practices

### Do
- Implement principle of least privilege
- Use role-based access control
- Log all access attempts
- Regular access reviews
- Multi-factor authentication for sensitive access

### Don't
- Grant excessive permissions
- Share credentials
- Ignore access violations
- Skip authorization checks
- Hardcode access rules

## Monitoring

### Metrics
- Authorization success/failure rate
- Access denial rate
- Role usage statistics
- Permission usage patterns
- Suspicious access patterns

### Alerting
- High failure rate alerts
- Privilege escalation attempts
- Unusual access patterns
- Access from unusual locations
- Multiple failed attempts

## Contact

For questions about access control:
- Security Team: security@aegis-lens.local
- IAM Team: iam@aegis-lens.local
