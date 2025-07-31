# 🚀 Lista Obecności - Production Deployment Guide

This guide covers deploying the Lista Obecności system to production with proper security, monitoring, and backup systems.

## 📋 Prerequisites

- Docker and Docker Compose installed
- Domain name with DNS configured
- SSL certificate (Let's Encrypt recommended)
- SMTP email service (Gmail, Outlook, or dedicated SMTP server)

## 🔧 Initial Setup

### 1. Environment Configuration

Create a `.env` file in the project root:

```bash
# Security
SECRET_KEY=your-very-long-random-secret-key-at-least-32-characters-long
JWT_SECRET_KEY=another-different-secret-key-for-jwt-tokens
DEBUG=false

# Database
DATABASE_URL=sqlite:///./data/shifts.db

# Email Configuration (Gmail example)
EMAIL_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com
SENDER_NAME=Lista Obecności System

# Admin Account
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=secure-admin-password

# CORS Settings
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# App Version
APP_CURRENT_VERSION=2.0.0
PLAY_STORE_URL=https://play.google.com/store/apps/details?id=your.app.id

# Logging
LOG_LEVEL=INFO
LOG_TO_FILE=true

# Features
FEATURE_CSV_EXPORT=true
FEATURE_EMAIL_REPORTS=true
BACKUP_ENABLED=true
RATE_LIMIT_ENABLED=true
```

### 2. Gmail SMTP Setup

For Gmail SMTP:
1. Enable 2-Factor Authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use the App Password (not your regular password) in `SMTP_PASSWORD`

### 3. SSL Certificate Setup

Place your SSL certificates in the `ssl/` directory:
```
ssl/
├── fullchain.pem
├── privkey.pem
└── dhparam.pem (optional, for better security)
```

For Let's Encrypt:
```bash
# Install certbot
sudo apt install certbot

# Get certificate
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/
sudo chown $USER:$USER ssl/*
```

## 🐳 Docker Deployment

### 1. Build and Start Services

```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 2. Services Overview

- **lista-obecnosci-api** (port 8000): Mobile API endpoints with JWT authentication
- **lista-obecnosci-web** (port 8002): Web admin panel with session authentication  
- **nginx** (ports 80/443): Reverse proxy with SSL termination and rate limiting

### 3. Initial Database Setup

```bash
# Initialize database
docker-compose exec lista-obecnosci-api python init_db.py

# Create first backup
docker-compose exec lista-obecnosci-api python backup_db.py backup
```

## 🔐 Security Checklist

### Authentication & Authorization
- ✅ JWT authentication for mobile API
- ✅ Session-based authentication for web panel
- ✅ Protected admin endpoints
- ✅ Secure password hashing (bcrypt)
- ✅ Rate limiting on API endpoints

### Network Security
- ✅ HTTPS/SSL encryption
- ✅ CORS configuration
- ✅ Reverse proxy with Nginx
- ✅ Security headers (X-Frame-Options, etc.)

### Data Protection
- ✅ Database encryption at rest (filesystem level)
- ✅ Secure session management
- ✅ Input validation and sanitization
- ✅ SQL injection protection (SQLAlchemy ORM)

## 📊 Monitoring & Logging

### Log Files Location
```
logs/
├── app.log         # Application logs
├── error.log       # Error logs only  
├── access.log      # HTTP access logs
└── email.log       # Email service logs
```

### Log Rotation
Logs are automatically rotated when they reach 10MB, keeping 5 backup files.

### Monitoring Commands
```bash
# View real-time logs
docker-compose logs -f

# Check application health
curl https://your-domain.com/auth/status

# Monitor resource usage
docker stats

# Check email configuration
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     https://your-domain.com/email/test-connection
```

## 💾 Backup & Recovery

### Automated Backups

Backups are created automatically using the built-in backup system:

```bash
# Manual backup
docker-compose exec lista-obecnosci-api python backup_db.py backup

# List backups
docker-compose exec lista-obecnosci-api python backup_db.py list

# Restore from backup
docker-compose exec lista-obecnosci-api python backup_db.py restore --backup-file backups/lista_obecnosci_backup_20250131_120000.db.gz
```

### Backup Strategy
- **Frequency**: Daily automated backups at 2 AM
- **Retention**: 30 days or minimum 10 backups
- **Storage**: Local filesystem (consider external storage for production)
- **Compression**: gzip compression to save space

### External Backup Setup

For production, consider backing up to external storage:

```bash
# Example: rsync to remote server
rsync -av --delete backups/ user@backup-server:/path/to/backups/

# Example: AWS S3
aws s3 sync backups/ s3://your-backup-bucket/lista-obecnosci/
```

## 📱 Mobile App Configuration

### API Endpoints for Mobile

- **Base URL**: `https://your-domain.com/api/`
- **Authentication**: JWT Bearer tokens
- **Content-Type**: `application/json`

### Key Endpoints
```
POST /api/auth/login              # Login
GET  /api/mobile-config           # App configuration
POST /api/start                   # Start work shift
POST /api/stop                    # Stop work shift
GET  /api/logs/{worker_id}        # Get work logs
```

### Remote Configuration
Update mobile app features without app updates:
```bash
curl -X POST https://your-domain.com/mobile-config \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "timer_enabled": true,
       "gps_verification": true,
       "offline_mode": true
     }'
```

## 🔄 Updates & Maintenance

### Application Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose build
docker-compose up -d

# Check health after update
curl https://your-domain.com/auth/status
```

### Database Migrations
```bash
# Backup before migration
docker-compose exec lista-obecnosci-api python backup_db.py backup

# Run migrations (if any)
docker-compose exec lista-obecnosci-api python migrate_db.py

# Verify migration
docker-compose exec lista-obecnosci-api python -c "import models; print('Models OK')"
```

### SSL Certificate Renewal
```bash
# Renew Let's Encrypt certificate
sudo certbot renew

# Update Docker certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/

# Restart nginx
docker-compose restart nginx
```

## 🚨 Troubleshooting

### Common Issues

1. **Database locked error**
   ```bash
   # Check for long-running processes
   docker-compose exec lista-obecnosci-api python -c "
   import sqlite3; 
   conn = sqlite3.connect('shifts.db');
   print('Database accessible')
   "
   ```

2. **Email sending fails**
   ```bash
   # Test SMTP connection
   docker-compose exec lista-obecnosci-api python -c "
   from email_service import test_smtp_connection;
   print(test_smtp_connection())
   "
   ```

3. **High memory usage**
   ```bash
   # Check container stats
   docker stats

   # Restart services if needed
   docker-compose restart
   ```

4. **Mobile app can't connect**
   ```bash
   # Check API health
   curl https://your-domain.com/api/mobile-config

   # Check authentication
   curl -X POST https://your-domain.com/api/auth/login \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=admin&password=your-password"
   ```

### Log Analysis
```bash
# Check for errors
docker-compose logs | grep ERROR

# Monitor authentication attempts
docker-compose logs | grep "Auth event"

# Check email issues
docker-compose logs | grep "SMTP"
```

## 📈 Performance Optimization

### Database Optimization
```bash
# Vacuum database periodically
docker-compose exec lista-obecnosci-api python -c "
import sqlite3;
conn = sqlite3.connect('shifts.db');
conn.execute('VACUUM');
conn.close()
"
```

### Cache Headers (in nginx.conf)
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 📞 Support & Maintenance

### Health Checks
- Application: `https://your-domain.com/auth/status`
- API Documentation: `https://your-domain.com/docs`
- Email Test: Admin panel → Email configuration

### Regular Maintenance Tasks
- [ ] Weekly: Check log files and cleanup if needed
- [ ] Monthly: Review and test backups
- [ ] Quarterly: Update dependencies and security patches
- [ ] Yearly: Renew SSL certificates and review security

---

## 🆘 Emergency Procedures

### System Recovery
1. Stop all services: `docker-compose down`
2. Restore from backup: `python backup_db.py restore --backup-file latest_backup.db.gz`
3. Start services: `docker-compose up -d`
4. Verify functionality: Test login and basic operations

### Data Loss Prevention
- Always backup before major changes
- Test restore procedures regularly
- Monitor disk space for backup storage
- Set up external backup sync for critical data

For additional support, check the application logs and GitHub repository issues.