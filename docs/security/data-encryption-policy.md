# Data Encryption Policy

## Overview
This document outlines the data encryption standards and implementation for the Aegis-Lens platform. All sensitive data must be encrypted at rest and in transit to protect against unauthorized access.

## Encryption Standards

### At Rest Encryption
- **Database**: AES-256 encryption for all sensitive fields
- **File Storage**: AES-256 encryption for uploaded files
- **Backups**: AES-256 encryption for all backup data
- **Logs**: Encryption for sensitive log entries

### In Transit Encryption
- **API Communication**: TLS 1.3
- **Database Connections**: TLS 1.3
- **Internal Service Communication**: mTLS
- **WebSocket**: WSS (WebSocket Secure)

## Implementation

### Database Encryption

#### Field-Level Encryption
```typescript
import crypto from 'crypto';

class EncryptionService {
  private algorithm = 'aes-256-gcm';
  private keyLength = 32;
  private ivLength = 16;
  private saltLength = 64;
  private tagLength = 16;
  private iterations = 100000;

  private getKey(password: string, salt: Buffer): Buffer {
    return crypto.pbkdf2Sync(
      password,
      salt,
      this.iterations,
      this.keyLength,
      'sha256'
    );
  }

  encrypt(plaintext: string, password: string): string {
    const salt = crypto.randomBytes(this.saltLength);
    const iv = crypto.randomBytes(this.ivLength);
    const key = this.getKey(password, salt);

    const cipher = crypto.createCipheriv(this.algorithm, key, iv);
    const encrypted = Buffer.concat([
      cipher.update(plaintext, 'utf8'),
      cipher.final()
    ]);

    const tag = cipher.getAuthTag();

    return Buffer.concat([salt, iv, tag, encrypted]).toString('base64');
  }

  decrypt(ciphertext: string, password: string): string {
    const buffer = Buffer.from(ciphertext, 'base64');
    const salt = buffer.slice(0, this.saltLength);
    const iv = buffer.slice(this.saltLength, this.saltLength + this.ivLength);
    const tag = buffer.slice(
      this.saltLength + this.ivLength,
      this.saltLength + this.ivLength + this.tagLength
    );
    const encrypted = buffer.slice(this.saltLength + this.ivLength + this.tagLength);

    const key = this.getKey(password, salt);

    const decipher = crypto.createDecipheriv(this.algorithm, key, iv);
    decipher.setAuthTag(tag);

    return decipher.update(encrypted) + decipher.final('utf8');
  }
}
```

#### Database Schema Example
```sql
CREATE TABLE candidates (
  id UUID PRIMARY KEY,
  candidate_code VARCHAR(50) UNIQUE NOT NULL,
  -- Encrypted fields
  encrypted_data TEXT NOT NULL, -- AES-256 encrypted JSON
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_candidate_code ON candidates(candidate_code);
```

### File Encryption

#### Upload Encryption
```typescript
import crypto from 'crypto';
import fs from 'fs';

class FileEncryptionService {
  private algorithm = 'aes-256-gcm';

  encryptFile(inputPath: string, outputPath: string, key: Buffer): void {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv(this.algorithm, key, iv);

    const input = fs.createReadStream(inputPath);
    const output = fs.createWriteStream(outputPath);

    // Write IV first
    output.write(iv);

    input.pipe(cipher).pipe(output);
  }

  decryptFile(inputPath: string, outputPath: string, key: Buffer): void {
    const input = fs.createReadStream(inputPath);
    const output = fs.createWriteStream(outputPath);

    // Read IV first
    const iv = input.read(16);

    const decipher = crypto.createDecipheriv(this.algorithm, key, iv);
    input.pipe(decipher).pipe(output);
  }
}
```

### API Encryption

#### Request/Response Encryption
```typescript
import crypto from 'crypto';

class ApiEncryptionService {
  private algorithm = 'aes-256-gcm';

  encryptPayload(payload: any, key: Buffer): string {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv(this.algorithm, key, iv);

    const encrypted = Buffer.concat([
      cipher.update(JSON.stringify(payload), 'utf8'),
      cipher.final()
    ]);

    const tag = cipher.getAuthTag();

    return Buffer.concat([iv, tag, encrypted]).toString('base64');
  }

  decryptPayload(ciphertext: string, key: Buffer): any {
    const buffer = Buffer.from(ciphertext, 'base64');
    const iv = buffer.slice(0, 16);
    const tag = buffer.slice(16, 32);
    const encrypted = buffer.slice(32);

    const decipher = crypto.createDecipheriv(this.algorithm, key, iv);
    decipher.setAuthTag(tag);

    const decrypted = decipher.update(encrypted) + decipher.final('utf8');
    return JSON.parse(decrypted);
  }
}
```

## Key Management

### Key Rotation
- Rotate加密 keys every 90 days
- Maintain key history for data decryption
- Automated key rotation via CI/CD

### Key Storage
- Store keys in Kubernetes Secrets
- Use Hardware Security Module (HSM) for production
- Never hardcode keys in application code

### Key Access
- Principle of least privilege
- Audit key access logs
- Multi-factor authentication for key access

## Compliance

### Regulatory Requirements
- **GDPR**: Article 32 - Security of processing
- **HIPAA**: 45 CFR § 164.312 - Technical safeguards
- **PCI DSS**: Requirement 3 - Protect stored cardholder data
- **SOC 2**: CC6.1 - Logical and physical access controls

### Encryption Verification
- Regular encryption strength audits
- Penetration testing for encryption vulnerabilities
- Compliance certification reviews

## Monitoring

### Encryption Metrics
- Encryption/decryption latency
- Key rotation status
- Encryption key usage statistics
- Failed decryption attempts

### Alerting
- Alert on encryption failures
- Alert on key expiration
- Alert on unauthorized key access attempts
- Alert on weak encryption usage

## Best Practices

### Do
- Use industry-standard encryption algorithms
- Implement proper key management
- Encrypt data at rest and in transit
- Regularly rotate encryption keys
- Monitor encryption performance

### Don't
- Use deprecated encryption algorithms
- Store encryption keys in code
- Use weak key lengths
- Ignore encryption failures
- Skip encryption for performance

## Contact

For questions about encryption implementation or to report issues:
- Security Team: security@aegis-lens.local
- Infrastructure Team: infra@aegis-lens.local
