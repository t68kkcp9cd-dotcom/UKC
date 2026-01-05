# Ultimate Kitchen Compendium - Installation Guide

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Pre-Installation Setup](#pre-installation-setup)
3. [Installation Methods](#installation-methods)
4. [Configuration](#configuration)
5. [SSL/TLS Setup](#ssltls-setup)
6. [Post-Installation](#post-installation)
7. [Verification](#verification)
8. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- **Operating System**: Ubuntu 20.04 LTS, Debian 11, CentOS 8
- **Memory**: 4GB RAM
- **Storage**: 20GB free disk space
- **Network**: Stable internet connection
- **Processor**: 2+ CPU cores

### Recommended Requirements
- **Operating System**: Ubuntu 22.04 LTS
- **Memory**: 8GB RAM
- **Storage**: 50GB SSD
- **Network**: 100Mbps connection
- **Processor**: 4+ CPU cores (Intel Xeon E5-2630 v3 or better)

### Hardware Recommendations

#### Low-End Hardware (Development)
- **CPU**: Intel i3 or AMD equivalent
- **RAM**: 4GB
- **Storage**: 20GB HDD/SSD
- **Use Case**: Development, testing, small households

#### Production Hardware
- **CPU**: Intel Xeon E5-2630 v3 or better
- **RAM**: 8-16GB
- **Storage**: 50GB+ SSD
- **Use Case**: Production deployment, multiple users

#### High-End Hardware (Enterprise)
- **CPU**: 8+ cores
- **RAM**: 32GB+
- **Storage**: 100GB+ NVMe SSD
- **Use Case**: Large households, enterprise use

## Pre-Installation Setup

### 1. System Update

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### 2. Install Required Packages

```bash
# Ubuntu/Debian
sudo apt install -y \
    curl \
    git \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# CentOS/RHEL
sudo yum install -y \
    curl \
    git \
    gcc \
    make \
    openssl
```

### 3. Install Docker

```bash
# Official Docker installation script
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### 4. Install Docker Compose

```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

### 5. System Configuration

#### Configure Firewall
```bash
# Install UFW (Ubuntu/Debian)
sudo apt install ufw

# Allow SSH (important!)
sudo ufw allow ssh

# Allow web traffic
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow API traffic
sudo ufw allow 8000/tcp

# Enable firewall
sudo ufw enable
```

#### Configure System Limits
```bash
# Edit system limits
sudo tee /etc/sysctl.d/99-ukc.conf << 'EOF'
# Increase file descriptors
fs.file-max = 2097152

# Optimize network performance
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 65536 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728

# Enable TCP BBR congestion control
net.core.default_qdisc = fq
net.ipv4.tcp_congestion_control = bbr

# Security improvements
net.ipv4.tcp_syncookies = 1
net.ipv4.ip_forward = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0
EOF

# Apply changes
sudo sysctl -p /etc/sysctl.d/99-ukc.conf
```

#### Configure Security Limits
```bash
# Edit security limits
sudo tee /etc/security/limits.d/99-ukc.conf << 'EOF'
# Increase file descriptors
* soft nofile 65536
* hard nofile 65536

# Increase processes
* soft nproc 32768
* hard nproc 32768
EOF
```

## Installation Methods

### Method 1: Automated Script (Recommended)

#### Download and Run
```bash
# Download setup script
curl -fsSL https://raw.githubusercontent.com/your-repo/ukc/main/setup-ukc.sh -o setup-ukc.sh

# Make executable
chmod +x setup-ukc.sh

# Run as root
sudo ./setup-ukc.sh
```

#### Script Options
```bash
# Custom installation path
sudo ./setup-ukc.sh --path /home/user/ukc

# Development environment
sudo ./setup-ukc.sh --environment development

# Skip prerequisite checks
sudo ./setup-ukc.sh --skip-checks

# Custom database password
sudo ./setup-ukc.sh --db-password "your-secure-password"
```

#### What the Script Does
1. Checks system requirements
2. Creates directory structure
3. Generates secure passwords
4. Creates configuration files
5. Pulls Docker images
6. Starts services
7. Sets up monitoring
8. Creates backup scripts

### Method 2: Manual Docker Compose

#### Create Directory Structure
```bash
# Create project directory
mkdir -p /opt/ukc
cd /opt/ukc

# Create subdirectories
mkdir -p {backend,nginx,postgres,redis,ollama,logs,uploads,ssl,backup,monitoring}
```

#### Create Environment File
```bash
cat > .env << 'EOF'
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

#### Create Docker Compose File
```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  app:
    image: ukc/backend:latest
    container_name: ukc-app
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql+asyncpg://ukc:${DB_PASSWORD}@db:5432/ukc_db
      - REDIS_URL=redis://redis:6379/0
      - OLLAMA_BASE_URL=http://ollama:11434
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - JWT_ALGORITHM=HS256
      - JWT_EXPIRATION_MINUTES=10080
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    depends_on:
      - db
      - redis
    networks:
      - ukc-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15-alpine
    container_name: ukc-db
    restart: unless-stopped
    environment:
      - POSTGRES_USER=ukc
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=ukc_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - ukc-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ukc"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: ukc-redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - ukc-network

  ollama:
    image: ollama/ollama:latest
    container_name: ukc-ollama
    restart: unless-stopped
    volumes:
      - ollama_models:/root/.ollama
    ports:
      - "11434:11434"
    networks:
      - ukc-network
    deploy:
      resources:
        limits:
          memory: 6G

volumes:
  postgres_data:
  redis_data:
  ollama_models:

networks:
  ukc-network:
    driver: bridge
EOF
```

#### Start Services
```bash
# Pull Docker images
docker-compose pull

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

### Method 3: Development Setup

#### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Node.js 18+

#### Backend Setup
```bash
# Clone repository
git clone https://github.com/your-repo/ukc.git
cd ukc/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements/dev.txt

# Create environment file
cp .env.template .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
# Navigate to frontend
cd ../frontend

# Install dependencies
npm install

# Start development server
npm start
```

#### Mobile Development
```bash
# iOS
cd mobile/ios
open UltimateKitchenCompendium.xcworkspace

# Android
cd mobile/android
./gradlew build
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_PASSWORD` | PostgreSQL password | Auto-generated |
| `JWT_SECRET_KEY` | JWT signing key | Auto-generated |
| `ENVIRONMENT` | Environment | production |
| `DEBUG` | Debug mode | false |
| `OLLAMA_BASE_URL` | Ollama API endpoint | http://ollama:11434 |
| `ENABLE_AI_FEATURES` | Enable AI features | true |
| `RATE_LIMIT_PER_MINUTE` | API rate limit | 60 |

### Database Configuration

#### PostgreSQL Optimization
```sql
-- Add to postgresql.conf
shared_buffers = 8GB
effective_cache_size = 24GB
work_mem = 64MB
maintenance_work_mem = 2GB
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

### Redis Configuration

```bash
# Redis configuration
redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
```

### Logging Configuration

```python
# Logging setup
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
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

# Auto-renewal
sudo certbot renew --dry-run
```

### nginx SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Post-Installation

### 1. Initial Setup

```bash
# Create admin user
docker-compose exec app python -c "
from app.database import init_db
from app.models.user import User
from app.services.auth_service import AuthService
import asyncio

async def create_admin():
    await init_db()
    # Create admin user logic here

asyncio.run(create_admin())
"
```

### 2. Configure Email (Optional)

```bash
# Add to .env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourdomain.com
```

### 3. Configure Backups

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p /opt/ukc/backup/$DATE

# Database backup
docker-compose exec -T db pg_dump -U ukc ukc_db > /opt/ukc/backup/$DATE/database.sql

# Uploads backup
tar -czf /opt/ukc/backup/$DATE/uploads.tar.gz -C /opt/ukc uploads/

# Configuration backup
cp /opt/ukc/.env /opt/ukc/backup/$DATE/

# Keep last 7 days
find /opt/ukc/backup/ -type d -name "20*" -mtime +7 -exec rm -rf {} \;

echo "Backup completed: /opt/ukc/backup/$DATE"
EOF

chmod +x backup.sh

# Schedule with cron
echo "0 2 * * * /opt/ukc/backup.sh" | crontab -
```

### 4. Setup Monitoring

```bash
# Create monitoring stack
cd /opt/ukc
cat > monitoring-compose.yml << 'EOF'
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: ukc-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana:latest
    container_name: ukc-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  prometheus_data:
  grafana_data:
EOF

# Start monitoring
docker-compose -f monitoring-compose.yml up -d
```

## Verification

### 1. Service Health Check

```bash
# Check all services
docker-compose ps

# Check logs
docker-compose logs --tail=50

# Test API
curl http://localhost:8000/health
```

### 2. Database Connectivity

```bash
# Test database
docker-compose exec db pg_isready -U ukc

# Check database logs
docker-compose logs db
```

### 3. Redis Connectivity

```bash
# Test Redis
docker-compose exec redis redis-cli ping

# Check Redis logs
docker-compose logs redis
```

### 4. AI Service Check

```bash
# Test Ollama
curl http://localhost:11434/api/tags

# Download models
docker-compose exec ollama ollama pull phi3:mini
docker-compose exec ollama ollama pull llama2:7b
```

## Troubleshooting

### Common Issues

#### Docker Issues
```bash
# Check Docker status
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker

# Check Docker logs
journalctl -u docker.service
```

#### Port Conflicts
```bash
# Check port usage
sudo netstat -tlnp | grep :8000

# Change port in docker-compose.yml
ports:
  - "8080:8000"  # Change 8080 to desired port
```

#### Database Issues
```bash
# Reset database (WARNING: Data loss)
docker-compose down -v
docker-compose up -d

# Check database logs
docker-compose logs db

# Connect to database
docker-compose exec db psql -U ukc -d ukc_db
```

#### Memory Issues
```bash
# Check memory usage
free -h
docker stats

# Reduce memory usage
# Edit docker-compose.yml to reduce limits
```

### Performance Optimization

#### Database Optimization
```sql
-- Run in PostgreSQL
VACUUM ANALYZE;
REINDEX DATABASE ukc_db;
```

#### Application Optimization
```bash
# Increase worker processes
WORKERS=8

# Enable caching
ENABLE_REDIS_CACHE=true
```

#### System Optimization
```bash
# Increase file limits
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf
```

### Log Analysis

#### Application Logs
```bash
# View application logs
docker-compose logs -f app

# Search for errors
docker-compose logs app | grep ERROR

# Export logs
docker-compose logs app > app_logs.txt
```

#### System Logs
```bash
# System logs
journalctl -f

# Docker logs
journalctl -u docker.service -f
```

### Support Resources

#### Documentation
- **API Docs**: http://localhost:8000/docs
- **GitHub**: https://github.com/your-repo/ukc
- **Website**: https://ultimatekitchencompendium.com

#### Community Support
- **Discord**: [Join our server](https://discord.gg/ukc)
- **Reddit**: r/UltimateKitchenCompendium
- **Email**: support@ultimatekitchencompendium.com

---

**Your Ultimate Kitchen Compendium installation is now complete! Proceed to the [Quick Start Guide](QUICK_START_GUIDE.md) to begin using the system.**