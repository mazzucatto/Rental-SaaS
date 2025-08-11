# Installation Guide - Rental SaaS

This comprehensive guide will walk you through the installation and configuration of Rental SaaS on various environments.

## Table of Contents

- [System Requirements](#system-requirements)
- [Quick Start (Docker)](#quick-start-docker)
- [Development Setup](#development-setup)
- [Production Deployment](#production-deployment)
- [Manual Installation](#manual-installation)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

## System Requirements

### Minimum Requirements

- **CPU:** 2 cores
- **RAM:** 4GB
- **Storage:** 20GB free space
- **OS:** Linux (Ubuntu 20.04+), macOS, Windows 10+

### Recommended Requirements

- **CPU:** 4+ cores
- **RAM:** 8GB+
- **Storage:** 50GB+ SSD
- **OS:** Ubuntu 22.04 LTS

### Software Dependencies

- **Docker:** 20.10+
- **Docker Compose:** 2.0+
- **Git:** 2.30+
- **Make:** 4.0+ (optional, for convenience commands)

## Quick Start (Docker)

The fastest way to get Rental SaaS running is using Docker Compose.

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/rental-saas.git
cd rental-saas
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration (see Configuration section for details)
nano .env
```

### 3. Start the Application

```bash
# Using Make (recommended)
make setup
make prod

# Or using Docker Compose directly
docker-compose up -d
```

### 4. Access the Application

- **Frontend:** http://localhost
- **API:** http://localhost:5000
- **Database Admin:** http://localhost:8080 (Adminer)

### 5. Create Your First Account

1. Open http://localhost in your browser
2. Click "Create Account"
3. Fill in your company and admin user details
4. Start using the system!

## Development Setup

For development with hot-reload and debugging capabilities.

### 1. Prerequisites

Install the following on your development machine:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip nodejs npm postgresql-client

# macOS (using Homebrew)
brew install python@3.11 node postgresql

# Windows (using Chocolatey)
choco install python nodejs postgresql
```

### 2. Clone and Setup

```bash
git clone https://github.com/your-username/rental-saas.git
cd rental-saas
```

### 3. Start Infrastructure Services

```bash
# Start only database and cache services
make dev

# Or manually
docker-compose -f docker-compose.dev.yml up -d
```

### 4. Setup Backend

```bash
cd backend/rental_api

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://rental_user:rental_password@localhost:5432/rental_saas_dev"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="your-development-secret-key"
export JWT_SECRET_KEY="your-development-jwt-key"

# Run database migrations
python -c "from src.main import app, db; app.app_context().push(); db.create_all()"

# Start backend server
python src/main.py
```

### 5. Setup Frontend

```bash
# Open new terminal
cd frontend/rental-frontend

# Install dependencies
npm install
# or
pnpm install

# Start development server
npm run dev
# or
pnpm run dev
```

### 6. Access Development Environment

- **Frontend:** http://localhost:5173 (Vite dev server)
- **Backend:** http://localhost:5000
- **Database:** localhost:5432
- **Redis:** localhost:6379
- **Adminer:** http://localhost:8080
- **MailHog:** http://localhost:8025

## Production Deployment

### Option 1: Docker Compose (Recommended)

#### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### 2. Application Deployment

```bash
# Clone repository
git clone https://github.com/your-username/rental-saas.git
cd rental-saas

# Configure for production
cp .env.example .env
nano .env  # Edit with production values

# Start production environment
make prod

# Or manually
docker-compose --profile production up -d
```

#### 3. SSL/HTTPS Setup

```bash
# Install Certbot
sudo apt install certbot

# Generate SSL certificate
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates to nginx directory
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/

# Update nginx configuration
nano nginx/conf.d/default.conf

# Restart nginx
docker-compose restart nginx
```

### Option 2: Kubernetes

#### 1. Prepare Kubernetes Manifests

```bash
# Create namespace
kubectl create namespace rental-saas

# Create secrets
kubectl create secret generic rental-secrets \
  --from-literal=postgres-password=your-secure-password \
  --from-literal=redis-password=your-redis-password \
  --from-literal=secret-key=your-secret-key \
  --from-literal=jwt-secret=your-jwt-secret \
  -n rental-saas

# Apply manifests
kubectl apply -f k8s/ -n rental-saas
```

#### 2. Configure Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rental-saas-ingress
  namespace: rental-saas
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - yourdomain.com
    secretName: rental-saas-tls
  rules:
  - host: yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
```

### Option 3: Cloud Platforms

#### AWS ECS

```bash
# Build and push images
docker build -t your-registry/rental-backend backend/rental_api/
docker build -t your-registry/rental-frontend frontend/rental-frontend/

docker push your-registry/rental-backend
docker push your-registry/rental-frontend

# Deploy using ECS CLI or CloudFormation
```

#### Google Cloud Run

```bash
# Deploy backend
gcloud run deploy rental-backend \
  --image your-registry/rental-backend \
  --platform managed \
  --region us-central1

# Deploy frontend
gcloud run deploy rental-frontend \
  --image your-registry/rental-frontend \
  --platform managed \
  --region us-central1
```

## Manual Installation

For environments where Docker is not available.

### 1. Install System Dependencies

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip nodejs npm nginx postgresql redis-server
```

#### CentOS/RHEL

```bash
sudo yum install -y python3.11 python3-pip nodejs npm nginx postgresql-server redis
```

### 2. Setup PostgreSQL

```bash
# Initialize database
sudo postgresql-setup initdb

# Start and enable services
sudo systemctl start postgresql redis
sudo systemctl enable postgresql redis

# Create database and user
sudo -u postgres psql
CREATE DATABASE rental_saas;
CREATE USER rental_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE rental_saas TO rental_user;
\q
```

### 3. Setup Backend

```bash
# Create application user
sudo useradd -m -s /bin/bash rental

# Switch to application user
sudo su - rental

# Clone repository
git clone https://github.com/your-username/rental-saas.git
cd rental-saas/backend/rental_api

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env

# Initialize database
python -c "from src.main import app, db; app.app_context().push(); db.create_all()"
```

### 4. Setup Frontend

```bash
cd ../../frontend/rental-frontend

# Install dependencies
npm install

# Build for production
npm run build
```

### 5. Configure Nginx

```nginx
# /etc/nginx/sites-available/rental-saas
server {
    listen 80;
    server_name yourdomain.com;
    
    # Frontend
    location / {
        root /home/rental/rental-saas/frontend/rental-frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # API
    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/rental-saas /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. Setup Systemd Services

#### Backend Service

```ini
# /etc/systemd/system/rental-backend.service
[Unit]
Description=Rental SaaS Backend
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=rental
WorkingDirectory=/home/rental/rental-saas/backend/rental_api
Environment=PATH=/home/rental/rental-saas/backend/rental_api/venv/bin
ExecStart=/home/rental/rental-saas/backend/rental_api/venv/bin/python src/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable rental-backend
sudo systemctl start rental-backend
```

## Configuration

### Environment Variables

#### Required Variables

```env
# Database
DATABASE_URL=postgresql://user:password@host:port/database
POSTGRES_DB=rental_saas
POSTGRES_USER=rental_user
POSTGRES_PASSWORD=secure_password

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=redis_password

# Security
SECRET_KEY=your-super-secret-key-minimum-32-characters
JWT_SECRET_KEY=your-jwt-secret-key-minimum-32-characters

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
```

#### Optional Variables

```env
# Application
FLASK_ENV=production
DEBUG=false
CORS_ORIGINS=https://yourdomain.com

# File Upload
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=/app/uploads

# Timezone
TZ=America/Sao_Paulo

# Frontend
VITE_API_URL=https://yourdomain.com/api
```

### Database Configuration

#### PostgreSQL Optimization

```sql
-- /etc/postgresql/15/main/postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

#### Connection Pooling

```python
# config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'max_overflow': 20
}
```

### Redis Configuration

```conf
# /etc/redis/redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### Nginx Configuration

#### Production Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    
    # Frontend
    location / {
        root /var/www/rental-saas;
        try_files $uri $uri/ /index.html;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API
    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U rental_user -d rental_saas

# Check logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

#### 2. Redis Connection Failed

```bash
# Check Redis status
sudo systemctl status redis

# Test connection
redis-cli ping

# Check logs
sudo tail -f /var/log/redis/redis-server.log
```

#### 3. Frontend Not Loading

```bash
# Check nginx status
sudo systemctl status nginx

# Check nginx configuration
sudo nginx -t

# Check logs
sudo tail -f /var/log/nginx/error.log
```

#### 4. Backend API Errors

```bash
# Check backend service
sudo systemctl status rental-backend

# Check logs
sudo journalctl -u rental-backend -f

# Check application logs
tail -f /home/rental/rental-saas/backend/rental_api/logs/app.log
```

#### 5. Docker Issues

```bash
# Check container status
docker-compose ps

# Check logs
docker-compose logs -f [service_name]

# Restart services
docker-compose restart

# Clean rebuild
docker-compose down -v
docker-compose up -d --build
```

### Performance Issues

#### 1. Slow Database Queries

```sql
-- Enable query logging
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();

-- Analyze slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

#### 2. High Memory Usage

```bash
# Check memory usage
free -h
docker stats

# Optimize PostgreSQL
# Reduce shared_buffers if needed
# Adjust work_mem and maintenance_work_mem
```

#### 3. High CPU Usage

```bash
# Check processes
top
htop

# Check database activity
SELECT * FROM pg_stat_activity WHERE state = 'active';

# Optimize queries and add indexes
```

### Security Issues

#### 1. SSL Certificate Problems

```bash
# Check certificate validity
openssl x509 -in /path/to/cert.pem -text -noout

# Renew Let's Encrypt certificate
sudo certbot renew

# Test SSL configuration
curl -I https://yourdomain.com
```

#### 2. Authentication Issues

```bash
# Check JWT configuration
# Verify SECRET_KEY and JWT_SECRET_KEY are set
# Check token expiration settings

# Reset user password
python -c "
from src.main import app, db
from src.models.user import User
with app.app_context():
    user = User.query.filter_by(email='admin@example.com').first()
    user.set_password('newpassword')
    db.session.commit()
"
```

## Maintenance

### Regular Maintenance Tasks

#### 1. Database Maintenance

```bash
# Vacuum and analyze
sudo -u postgres psql rental_saas -c "VACUUM ANALYZE;"

# Backup database
pg_dump -h localhost -U rental_user rental_saas > backup_$(date +%Y%m%d).sql

# Monitor database size
sudo -u postgres psql rental_saas -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

#### 2. Log Rotation

```bash
# Configure logrotate
sudo nano /etc/logrotate.d/rental-saas

# Content:
/home/rental/rental-saas/backend/rental_api/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 rental rental
    postrotate
        systemctl reload rental-backend
    endscript
}
```

#### 3. System Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker-compose pull
docker-compose up -d

# Update application
git pull origin main
make prod-build
```

#### 4. Monitoring

```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check service status
systemctl status postgresql redis nginx rental-backend

# Check application health
curl http://localhost:5000/api/health
```

### Backup Strategy

#### 1. Database Backups

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups/database"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

pg_dump -h localhost -U rental_user rental_saas | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
```

#### 2. File Backups

```bash
# Backup uploaded files
rsync -av /home/rental/rental-saas/backend/rental_api/uploads/ /backups/uploads/

# Backup configuration
cp /home/rental/rental-saas/.env /backups/config/env_$DATE
```

#### 3. Automated Backups

```bash
# Add to crontab
crontab -e

# Daily database backup at 2 AM
0 2 * * * /home/rental/scripts/backup_database.sh

# Weekly full backup at 3 AM on Sundays
0 3 * * 0 /home/rental/scripts/backup_full.sh
```

### Scaling

#### 1. Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  backend:
    deploy:
      replicas: 3
  
  nginx:
    depends_on:
      - backend
    # Configure load balancing
```

#### 2. Database Scaling

```bash
# Read replicas
# Configure PostgreSQL streaming replication
# Update application to use read replicas for queries
```

#### 3. Caching

```bash
# Redis cluster
# Configure Redis Cluster for high availability
# Implement application-level caching
```

For additional support, please refer to:
- [Documentation](https://docs.rentalsaas.com)
- [GitHub Issues](https://github.com/rental-saas/issues)
- [Community Forum](https://community.rentalsaas.com)

