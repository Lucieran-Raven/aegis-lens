# SSL/TLS Configuration Policy

## Overview
This document outlines the SSL/TLS configuration standards for the Aegis-Lens platform. All network communications must use secure TLS protocols to protect data in transit.

## TLS Standards

### Protocol Versions
- **Required**: TLS 1.3
- **Allowed**: TLS 1.2 (with strong cipher suites)
- **Deprecated**: TLS 1.0, TLS 1.1, SSLv2, SSLv3

### Cipher Suites

#### TLS 1.3 Cipher Suites
```
TLS_AES_256_GCM_SHA384
TLS_CHACHA20_POLY1305_SHA256
TLS_AES_128_GCM_SHA256
```

#### TLS 1.2 Cipher Suites
```
ECDHE-RSA-AES256-GCM-SHA384
ECDHE-RSA-AES128-GCM-SHA256
ECDHE-RSA-CHACHA20-POLY1305
ECDHE-ECDSA-AES256-GCM-SHA384
ECDHE-ECDSA-AES128-GCM-SHA256
```

### Key Exchange
- **Preferred**: ECDHE (Elliptic Curve Diffie-Hellman Ephemeral)
- **Fallback**: DHE (Diffie-Hellman Ephemeral)
- **Prohibited**: Static RSA, Static DH

### Certificate Requirements
- **Algorithm**: RSA 2048-bit minimum, ECDSA P-256 preferred
- **Hash Algorithm**: SHA-256 or higher
- **Validity**: Maximum 1 year
- **CA**: Public CA or internal PKI

## Implementation

### Nginx Configuration
```nginx
# SSL/TLS Configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers on;

# TLS 1.3 Cipher Suites
ssl_ciphers 'TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256';

# TLS 1.2 Cipher Suites (fallback)
ssl_ciphers 'ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-GCM-SHA256';

# DH Parameters
ssl_dhparam /etc/nginx/dhparam.pem;

# Session Configuration
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/nginx/chain.pem;

# HSTS
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

# Security Headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### Kubernetes Ingress Configuration
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: aegis-lens-ingress
  namespace: aegis-lens
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/ssl-ciphers: "ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256"
    nginx.ingress.kubernetes.io/ssl-protocols: "TLSv1.2 TLSv1.3"
    nginx.ingress.kubernetes.io/ssl-prefer-server-ciphers: "true"
    nginx.ingress.kubernetes.io/hsts: "max-age=63072000; includeSubDomains; preload"
    nginx.ingress.kubernetes.io/hsts-include-subdomains: "true"
    nginx.ingress.kubernetes.io/hsts-preload: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - aegis-lens.local
    - candidate-ui.aegis-lens.local
    - hr-dashboard.aegis-lens.local
    secretName: tls-secrets
```

### Application Configuration (Node.js)
```typescript
import https from 'https';
import fs from 'fs';

const tlsOptions = {
  key: fs.readFileSync('/path/to/private-key.pem'),
  cert: fs.readFileSync('/path/to/certificate.pem'),
  ca: fs.readFileSync('/path/to/ca-chain.pem'),
  
  // Protocol configuration
  minVersion: 'TLSv1.2',
  maxVersion: 'TLSv1.3',
  
  // Cipher configuration
  ciphers: [
    'TLS_AES_256_GCM_SHA384',
    'TLS_CHACHA20_POLY1305_SHA256',
    'TLS_AES_128_GCM_SHA256',
    'ECDHE-RSA-AES256-GCM-SHA384',
    'ECDHE-RSA-AES128-GCM-SHA256'
  ].join(':'),
  
  // DH parameters
  dhparam: fs.readFileSync('/path/to/dhparam.pem'),
  
  // Session configuration
  sessionTimeout: 86400000, // 24 hours
  sessionCache: {
    maxSessions: 1000,
    ticketKeys: fs.readFileSync('/path/to/ticket-keys')
  },
  
  // OCSP stapling
  requestOCSP: true,
  
  // HSTS
  hsts: {
    maxAge: 63072000,
    includeSubDomains: true,
    preload: true
  }
};

const server = https.createServer(tlsOptions, app);
```

### Application Configuration (Python)
```python
import ssl

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

# Protocol configuration
context.minimum_version = ssl.TLSVersion.TLSv1_2
context.maximum_version = ssl.TLSVersion.TLSv1_3

# Cipher configuration
context.set_ciphers('ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256')

# Load certificates
context.load_cert_chain(
    certfile='/path/to/certificate.pem',
    keyfile='/path/to/private-key.pem'
)

# Load CA chain
context.load_verify_locations(cafile='/path/to/ca-chain.pem')

# DH parameters
context.load_dh_params('/path/to/dhparam.pem')

# Session configuration
context.session_timeout = 86400  # 24 hours

# OCSP stapling
context.ocsp_stapling = True
```

## Certificate Management

### Certificate Generation (Self-Signed for Development)
```bash
# Generate private key
openssl genrsa -out private-key.pem 2048

# Generate certificate signing request
openssl req -new -key private-key.pem -out csr.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=aegis-lens.local"

# Generate self-signed certificate
openssl x509 -req -days 365 -in csr.pem -signkey private-key.pem -out certificate.pem

# Generate CA bundle
cat certificate.pem > chain.pem
```

### Certificate Generation (Let's Encrypt)
```bash
# Install certbot
apt-get install certbot

# Generate certificate
certbot certonly --standalone \
  -d aegis-lens.local \
  -d candidate-ui.aegis-lens.local \
  -d hr-dashboard.aegis-lens.local \
  --email admin@aegis-lens.local \
  --agree-tos

# Certificate location
# /etc/letsencrypt/live/aegis-lens.local/fullchain.pem
# /etc/letsencrypt/live/aegis-lens.local/privkey.pem
```

### DH Parameters Generation
```bash
# Generate strong DH parameters (2048-bit)
openssl dhparam -out dhparam.pem 2048

# For higher security (4096-bit)
openssl dhparam -out dhparam.pem 4096
```

### Certificate Rotation
```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: aegis-lens-cert
  namespace: aegis-lens
spec:
  secretName: tls-secrets
  duration: 2160h # 90 days
  renewBefore: 720h # 30 days before expiration
  dnsNames:
  - aegis-lens.local
  - candidate-ui.aegis-lens.local
  - hr-dashboard.aegis-lens.local
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
```

## Monitoring

### Certificate Expiration Monitoring
```typescript
class CertificateMonitor {
  private checkExpiration(certPath: string): number {
    const cert = fs.readFileSync(certPath);
    const certInfo = new X509Certificate(cert);
    const expirationDate = new Date(certInfo.validTo);
    const today = new Date();
    const daysUntilExpiration = Math.floor(
      (expirationDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)
    );
    return daysUntilExpiration;
  }

  async monitorCertificates(): Promise<void> {
    const certificates = [
      '/etc/nginx/certificate.pem',
      '/etc/letsencrypt/live/aegis-lens.local/fullchain.pem'
    ];

    for (const certPath of certificates) {
      const daysUntilExpiration = this.checkExpiration(certPath);
      
      if (daysUntilExpiration < 30) {
        await this.alertCertificateExpiring(certPath, daysUntilExpiration);
      }
      
      if (daysUntilExpiration < 0) {
        await this.alertCertificateExpired(certPath);
      }
    }
  }
}
```

### SSL/TLS Configuration Testing
```bash
# Test SSL configuration
nmap --script ssl-enum-ciphers -p 443 aegis-lens.local

# Test SSL configuration with SSL Labs
curl https://www.ssllabs.com/ssltest/analyze.html?d=aegis-lens.local

# Check certificate information
openssl s_client -connect aegis-lens.local:443 -servername aegis-lens.local

# Check certificate chain
openssl s_client -connect aegis-lens.local:443 -showcerts

# Check TLS version
openssl s_client -connect aegis-lens.local:443 -tls1_2
openssl s_client -connect aegis-lens.local:443 -tls1_3
```

## Security Headers

### HSTS (HTTP Strict Transport Security)
```nginx
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
```

### CSP (Content Security Policy)
```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' wss: https:; frame-ancestors 'self';" always;
```

### X-Frame-Options
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
```

### X-Content-Type-Options
```nginx
add_header X-Content-Type-Options "nosniff" always;
```

### X-XSS-Protection
```nginx
add_header X-XSS-Protection "1; mode=block" always;
```

### Referrer-Policy
```nginx
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### Permissions-Policy
```nginx
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

## Compliance

### Regulatory Requirements
- **GDPR**: Article 32 - Security of processing
- **HIPAA**: 45 CFR § 164.312 - Transmission security
- **PCI DSS**: Requirement 4 - Encrypt transmission of cardholder data
- **SOC 2**: CC6.1 - Logical and physical access controls

### Security Standards
- **NIST**: SP 800-52 Rev. 2 - Guidelines for Securing TLS
- **OWASP**: TLS Configuration Best Practices
- **CIS**: Benchmark for NGINX

## Best Practices

### Do
- Use TLS 1.3 where possible
- Implement HSTS with preload
- Use strong cipher suites
- Monitor certificate expiration
- Implement certificate rotation
- Use OCSP stapling
- Implement security headers

### Don't
- Use deprecated protocols (SSLv2, SSLv3, TLS 1.0, TLS 1.1)
- Use weak cipher suites
- Ignore certificate expiration
- Use self-signed certificates in production
- Disable certificate validation
- Use static key exchange
- Skip security headers

## Troubleshooting

### Common Issues

#### Certificate Chain Errors
```bash
# Check certificate chain
openssl s_client -connect aegis-lens.local:443 -showcerts

# Verify certificate chain
openssl verify -CAfile /path/to/ca-bundle.pem /path/to/certificate.pem
```

#### Cipher Suite Errors
```bash
# Test specific cipher
openssl s_client -connect aegis-lens.local:443 -cipher ECDHE-RSA-AES256-GCM-SHA384

# List supported ciphers
openssl ciphers -v 'ECDHE-RSA-AES256-GCM-SHA384'
```

#### Protocol Version Errors
```bash
# Test TLS 1.2
openssl s_client -connect aegis-lens.local:443 -tls1_2

# Test TLS 1.3
openssl s_client -connect aegis-lens.local:443 -tls1_3
```

## Contact

For questions about SSL/TLS configuration:
- Security Team: security@aegis-lens.local
- Infrastructure Team: infra@aegis-lens.local
