# SSL Certificate Setup Guide

This guide covers SSL/TLS certificate setup for AEGIS LENS using Let's Encrypt with Certbot.

## Prerequisites

- Domain name pointed to your server
- Server with public IP address
- Root or sudo access
- Nginx installed

## Installation

### Install Certbot

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx
```

## Obtaining Certificate

### Automatic Nginx Configuration

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### Manual Configuration

```bash
sudo certbot certonly --nginx -d your-domain.com -d www.your-domain.com
```

## Certificate Locations

Certificates are installed in:
- Certificate: `/etc/letsencrypt/live/your-domain.com/fullchain.pem`
- Private Key: `/etc/letsencrypt/live/your-domain.com/privkey.pem`
- Chain: `/etc/letsencrypt/live/your-domain.com/chain.pem`

## Nginx Configuration

Update your Nginx configuration to use the certificates:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL settings (already in nginx.conf)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
}
```

## Auto-Renewal

Certbot automatically sets up a systemd timer or cron job for renewal. Verify:

```bash
sudo systemctl status certbot.timer
sudo certbot renew --dry-run
```

## Testing SSL Configuration

Test your SSL configuration:

```bash
# Check certificate
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# Online test
# Visit: https://www.ssllabs.com/ssltest/
```

## Docker Setup

For Docker deployments, mount the certificates:

```yaml
volumes:
  - /etc/letsencrypt:/etc/letsencrypt:ro
```

## Self-Signed Certificates (Development Only)

For local development, generate self-signed certificates:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem
```

## Troubleshooting

### Port 80 Blocked
Ensure port 80 is open for HTTP-01 challenge:
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### Renewal Failures
Check logs:
```bash
sudo journalctl -u certbot.timer
sudo certbot renew --force-renewal
```

## Security Best Practices

1. Use strong SSL/TLS configurations (TLS 1.2+ only)
2. Enable HSTS in production
3. Rotate certificates regularly
4. Monitor certificate expiration
5. Use certificate pinning for critical services
