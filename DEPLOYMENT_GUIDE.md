# Ultimate Kitchen Compendium - Deployment Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Hardware Requirements](#hardware-requirements)
3. [Installation Options](#installation-options)
4. [Quick Start](#quick-start)
5. [Manual Installation](#manual-installation)
6. [Proxmox VE Setup](#proxmox-ve-setup)
7. [Configuration](#configuration)
8. [SSL/TLS Setup](#ssltls-setup)
9. [Monitoring](#monitoring)
10. [Backup and Restore](#backup-and-restore)
11. [Troubleshooting](#troubleshooting)
12. [Performance Tuning](#performance-tuning)

## Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+)
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 20GB+ available disk space
- **Network**: Stable internet connection
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+

### Required Software
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
```

## Hardware Requirements

### Minimum Configuration (Development)
- **CPU**: 2 cores (Intel i3 or equivalent)
- **RAM**: 4GB
- **Storage**: 20GB SSD
- **Network**: 10 Mbps

### Recommended Configuration (Production)
- **CPU**: 4+ cores (Intel Xeon E5-2630 v3 or better)
- **RAM**: 8-16GB
- **Storage**: 50GB+ SSD
- **Network**: 100 Mbps

### Low-End Hardware Optimization
For systems with limited resources:
- Use CPU-only AI models
- Reduce database connection pool size
- Limit concurrent API requests
- Use Redis for caching

## Installation Options

### Option 1: Automated Installation (Recommended)
```bash
# Download and run the setup script
curl -fsSL https://raw.githubusercontent.com/your-repo/ukc/main/setup-ukc.sh | sudo bash

# Or download first, then run
curl -fsSL https://raw.githubusercontent.com/your-repo/ukc/main/setup-ukc.sh -o setup-ukc.sh
chmod +x setup-ukc.sh
sudo ./setup-ukc.sh
```

### Option 2: Docker Compose
```bash
# Clone repository
git clone https://github.com/your-repo/ukc.git
cd ukc

# Create environment file
cp .env.template .env
# Edit .env with your configuration

# Start services
docker-compose up -d
```

### Option 3: Manual Installation
Follow the step-by-step manual installation guide below.

## Quick Start

### 1. Using the Setup Script
```bash
# Quick start with defaults
sudo ./setup-ukc.sh

# Custom installation path
sudo ./setup-ukc.sh --path /home/user/ukc

# Development environment
sudo ./setup-ukc.sh --environment development
```

### 2. Verify Installation
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f app

# Test API
curl http://localhost:8000/health
```

### 3. Access Application
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## Manual Installation

### Step 1: System Preparation
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y curl git build-essential

# Install Docker (if not already installed)
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 2: Create Directory Structure
```bash
# Create installation directory
sudo mkdir -p /opt/ukc
cd /opt/ukc

# Create subdirectories
sudo mkdir -p {backend,nginx,postgres,redis,ollama,logs,uploads,ssl,backup,monitoring}
```

### Step 3: Configuration Files

#### Create .env file
```bash
cat > .env << EOF
# Database Configuration
DB_PASSWORD=$(openssl rand -base64 32)
POSTGRES_USER=ukc
POSTGRES_DB=ukc_db

# JWT Configuration
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=10080
JWT_REFRESH_EXPIRATION_DAYS=30

# Application Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Ollama Configuration
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_CHAT_MODEL=phi3:mini
OLLAMA_RECIPE_MODEL=llama2:7b
OLLAMA_TIMEOUT=60

# File Storage
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10

# Features
ENABLE_AI_FEATURES=true
ENABLE_GAMIFICATION=true
ENABLE_STORE_INTEGRATION=true
EOF
```

#### Create docker-compose.yml
Copy the docker-compose.yml file from the backend directory to /opt/ukc/

#### Create nginx configuration
```bash
cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;
    
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/rss+xml application/atom+xml image/svg+xml;
    
    upstream app {
        server app:8000;
    }
    
    server {
        listen 80;
        server_name _;
        
        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        location /ws {
            proxy_pass http://app;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
EOF
```

### Step 4: Start Services
```bash
# Pull Docker images
docker-compose pull

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

## Proxmox VE Setup

### Create LXC Container
```bash
# Create container template
pveam update
pveam download local debian-12-standard_12.2-1_amd64.tar.zst

# Create container
pct create 1001 /var/lib/vz/template/cache/debian-12-standard_12.2-1_amd64.tar.zst \
    --hostname ukc-server \
    --cores 2 \
    --memory 4096 \
    --swap 1024 \
    --storage local-lvm \
    --rootfs 20 \
    --net0 name=eth0,bridge=vmbr0,ip=dhcp \
    --unprivileged 1 \
    --features nesting=1

# Start container
pct start 1001
```

### Configure Container
```bash
# Enter container
pct enter 1001

# Install Docker
apt update && apt upgrade -y
apt install -y curl

curl -fsSL https://get.docker.com | sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_PASSWORD` | PostgreSQL password | Auto-generated |
| `JWT_SECRET_KEY` | JWT signing key | Auto-generated |
| `ENVIRONMENT` | Environment (development/production) | production |
| `DEBUG` | Debug mode | false |
| `OLLAMA_BASE_URL` | Ollama API endpoint | http://ollama:11434 |
| `ENABLE_AI_FEATURES` | Enable AI features | true |
| `ENABLE_GAMIFICATION` | Enable gamification | true |

### Database Configuration

#### PostgreSQL Optimization
```sql
-- Optimized for Intel Xeon E5-2630 v3, 32GB RAM
shared_buffers = 8GB
effective_cache_size = 24GB
work_mem = 64MB
max_connections = 100
```

#### Connection Pooling
```python
# SQLAlchemy configuration
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=300
)
```

## SSL/TLS Setup

### Development (Self-Signed)
```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/selfsigned.key \
    -out ssl/selfsigned.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

### Production (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com

# Update nginx configuration to use certificates
```

### nginx SSL Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://app;
        # ... proxy headers
    }
}
```

## Monitoring

### Prometheus Setup
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ukc-app'
    static_configs:
      - targets: ['app:8000']
    metrics_path: /metrics
```

### Grafana Dashboards
Import pre-configured dashboards:
- Application metrics
- Database performance
- System resources

### Health Checks
```bash
# Application health
curl http://localhost:8000/health

# Database connectivity
docker-compose exec db pg_isready -U ukc

# Redis connectivity
docker-compose exec redis redis-cli ping
```

## Backup and Restore

### Automated Backups
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p backup/$DATE

# Database backup
docker-compose exec -T db pg_dump -U ukc ukc_db > backup/$DATE/database.sql

# Uploads backup
tar -czf backup/$DATE/uploads.tar.gz uploads/

# Keep last 7 days
find backup/ -type d -name "20*" -mtime +7 -exec rm -rf {} \;
EOF

chmod +x backup.sh

# Schedule with cron
echo "0 2 * * * /opt/ukc/backup.sh" | crontab -
```

### Manual Backup
```bash
# Database
docker-compose exec db pg_dump -U ukc ukc_db > backup.sql

# Restore
docker-compose exec -T db psql -U ukc ukc_db < backup.sql
```

### Disaster Recovery
```bash
# Complete system backup
tar -czf ukc-backup.tar.gz /opt/ukc/

# Restore on new system
tar -xzf ukc-backup.tar.gz -C /
cd /opt/ukc
docker-compose up -d
```

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker-compose logs app

# Check configuration
docker-compose config

# Restart services
docker-compose down
docker-compose up -d
```

#### Database Connection Issues
```bash
# Check database logs
docker-compose logs db

# Test database connectivity
docker-compose exec db pg_isready -U ukc

# Reset database (WARNING: Data loss)
docker-compose down -v
docker-compose up -d
```

#### Memory Issues
```bash
# Check memory usage
free -h
docker stats

# Reduce memory usage
# - Lower PostgreSQL shared_buffers
# - Reduce worker processes
# - Use swap if necessary
```

#### Network Issues
```bash
# Check network connectivity
docker network ls
docker-compose exec app ping db

# Reset network
docker-compose down
docker network prune
docker-compose up -d
```

### Log Analysis
```bash
# Application logs
docker-compose logs -f app

# Database logs
docker-compose logs -f db

# All service logs
docker-compose logs -f
```

### Performance Issues
```bash
# Monitor resource usage
docker stats
htop

# Database performance
sudo -u postgres psql
checkpoint; analyze;

# Application profiling
# Enable debug mode for detailed logs
```

## Performance Tuning

### Database Optimization
```sql
-- Analyze tables
ANALYZE;

-- Update table statistics
VACUUM ANALYZE;

-- Check slow queries
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### Application Optimization
```python
# Enable query caching
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

@app.get("/api/v1/inventory")
@cache(expire=300)  # Cache for 5 minutes
def get_inventory():
    pass
```

### System Optimization
```bash
# Increase file limits
echo "fs.file-max = 2097152" >> /etc/sysctl.conf

# Optimize network
echo "net.core.rmem_max = 134217728" >> /etc/sysctl.conf
echo "net.core.wmem_max = 134217728" >> /etc/sysctl.conf
```

### Resource Monitoring
```bash
# Create monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
echo "=== System Resources ==="
free -h
echo ""
echo "=== Disk Usage ==="
df -h
echo ""
echo "=== Docker Resources ==="
docker system df
echo ""
echo "=== Top Processes ==="
ps aux --sort=-%mem | head -10
EOF

chmod +x monitor.sh
```

## Support and Maintenance

### Regular Maintenance Tasks
- Monitor disk usage
- Check log rotation
- Update Docker images
- Review security logs
- Test backup restoration

### Update Process
```bash
# Update Docker images
docker-compose pull

# Restart with new images
docker-compose up -d

# Clean old images
docker image prune -f
```

### Getting Help
- Check the troubleshooting section
- Review application logs
- Check GitHub issues
- Join community Discord/Reddit

---

For additional support, please refer to the main documentation or community forums.