# Ultimate Kitchen Compendium - Quick Start Guide

Get your kitchen management system up and running in under 15 minutes!

## ⚡ Prerequisites Checklist

Before you begin, ensure you have:
- [ ] A computer with Linux (Ubuntu 20.04+ recommended)
- [ ] Internet connection
- [ ] Basic command line knowledge
- [ ] 30 minutes of uninterrupted time

## 🚀 Installation Options

### Option A: Automated Setup (Recommended - 5 minutes)

Perfect for getting started quickly:

```bash
# 1. Download and run the setup script
curl -fsSL https://raw.githubusercontent.com/your-repo/ukc/main/setup-ukc.sh -o setup-ukc.sh
chmod +x setup-ukc.sh
sudo ./setup-ukc.sh

# 2. Follow the prompts
# The script will:
# - Install Docker if needed
# - Create necessary directories
# - Generate secure passwords
# - Start all services
# - Configure the system
```

**What happens during automated setup:**
1. Checks system requirements
2. Installs Docker and Docker Compose if needed
3. Creates `/opt/ukc` directory structure
4. Generates secure passwords and keys
5. Pulls Docker images
6. Starts all services
7. Runs database migrations
8. Sets up monitoring
9. Creates backup scripts

### Option B: Docker Compose (10 minutes)

For users who want more control:

```bash
# 1. Create project directory
mkdir -p ~/ukc && cd ~/ukc

# 2. Download docker-compose.yml
curl -O https://raw.githubusercontent.com/your-repo/ukc/main/docker-compose.yml

# 3. Create environment file
cat > .env << 'EOF'
# Generate secure passwords
DB_PASSWORD=$(openssl rand -base64 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Application settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Server settings
HOST=0.0.0.0
PORT=8000
EOF

# 4. Start services
docker-compose up -d

# 5. Wait for services to start
sleep 30

# 6. Check status
docker-compose ps
```

### Option C: Proxmox VE (15 minutes)

For Proxmox users:

```bash
# On Proxmox host:
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

pct start 1001
pct enter 1001

# Inside container:
apt update && apt install -y curl
curl -fsSL https://raw.githubusercontent.com/your-repo/ukc/main/setup-ukc.sh | bash
```

## ✅ Verification Steps

### 1. Check Service Health (1 minute)

```bash
# Check if containers are running
docker-compose ps

# Expected output:
# NAME                COMMAND                  SERVICE             STATUS              PORTS
# ukc-app             "python -m uvicorn..."   app                 running (healthy)   0.0.0.0:8000->8000/tcp
# ukc-db              "docker-entrypoint.s…"   db                  running (healthy)   5432/tcp
# ukc-redis           "docker-entrypoint.s…"   redis               running (healthy)   6379/tcp
# ukc-ollama          "/bin/ollama"            ollama              running             11434/tcp
```

### 2. Test API Connection (1 minute)

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "services": {
#     "database": {"status": "healthy"},
#     "redis": {"status": "healthy"},
#     "ollama": {"status": "healthy"}
#   }
# }
```

### 3. Access Web Interface (1 minute)

Open your browser and navigate to:
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 4. Create First User (2 minutes)

```bash
# Using the interactive API docs or:
curl -X POST "http://localhost:8000/api/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d '{
        "username": "admin",
        "email": "admin@example.com",
        "password": "your-secure-password-123"
    }'
```

### 5. Login and Test (1 minute)

```bash
# Get authentication token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d '{
        "username": "admin",
        "password": "your-secure-password-123"
    }'
```

## 📱 Mobile App Setup

### iOS App

1. **Download from App Store**
   - Search "Ultimate Kitchen Compendium"
   - Install the app

2. **Configure Connection**
   - Open app
   - Go to Settings
   - Enter server URL: `http://your-server-ip:8000`
   - Login with created credentials

### Android App

1. **Download from Google Play Store**
   - Search "Ultimate Kitchen Compendium"
   - Install the app

2. **Configure Connection**
   - Open app
   - Go to Settings
   - Enter server URL: `http://your-server-ip:8000`
   - Login with created credentials

## 🎯 First Actions

### 1. Add Your First Item

```bash
curl -X POST "http://localhost:8000/api/v1/inventory" \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Organic Tomatoes",
        "quantity": 5,
        "unit": "pieces",
        "location": "fridge",
        "expiration_date": "2024-12-31"
    }'
```

### 2. Create a Recipe

```bash
curl -X POST "http://localhost:8000/api/v1/recipes" \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "title": "Fresh Tomato Salad",
        "description": "Simple and delicious tomato salad",
        "prep_time": 10,
        "servings": 2,
        "difficulty": "easy",
        "ingredients": [
            {
                "name": "Organic Tomatoes",
                "quantity": 3,
                "unit": "pieces"
            }
        ],
        "steps": [
            {
                "step_number": 1,
                "instruction": "Wash and slice the tomatoes"
            }
        ]
    }'
```

### 3. Generate Shopping List

```bash
curl -X POST "http://localhost:8000/api/v1/shopping-lists" \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "list_name": "Weekly Shopping"
    }'
```

## 🔧 Essential Commands

### Daily Operations
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f app

# Restart services
docker-compose restart

# Update images
docker-compose pull
docker-compose up -d
```

### Monitoring
```bash
# Check resource usage
docker stats

# View all logs
docker-compose logs -f

# Check service health
curl http://localhost:8000/health
```

### Backup
```bash
# Quick backup
docker-compose exec db pg_dump -U ukc ukc_db > backup.sql

# Restore backup
docker-compose exec -T db psql -U ukc ukc_db < backup.sql
```

## 🛠️ Troubleshooting

### Service Won't Start
```bash
# Check logs for errors
docker-compose logs app

# Common issues:
# 1. Port 8000 already in use
# 2. Database connection failed
# 3. Insufficient memory

# Solutions:
# 1. Change port in docker-compose.yml
# 2. Check database: docker-compose logs db
# 3. Increase memory or reduce worker count
```

### Database Connection Failed
```bash
# Check database container
docker-compose logs db

# Test database connectivity
docker-compose exec db pg_isready -U ukc

# Reset database (WARNING: Data loss)
docker-compose down -v
docker-compose up -d
```

### AI Features Not Working
```bash
# Check Ollama container
docker-compose logs ollama

# Download AI models
docker-compose exec ollama ollama pull phi3:mini
docker-compose exec ollama ollama pull llama2:7b
```

### Mobile App Connection Issues
```bash
# Check network connectivity
ping your-server-ip

# Check firewall
sudo ufw status

# Allow port 8000
sudo ufw allow 8000
```

## 📊 Next Steps

1. **Explore Features**: Try all the features in the web interface
2. **Download Mobile Apps**: Get the apps from app stores
3. **Add Family Members**: Invite others to your household
4. **Scan Barcodes**: Use your phone to add items quickly
5. **Plan Meals**: Create your first meal plan
6. **Generate Shopping List**: Let the system create lists for you

## 📚 Learn More

- **Full User Guide**: [USER_GUIDE.md](USER_GUIDE.md)
- **Installation Guide**: [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
- **API Documentation**: http://localhost:8000/docs
- **Video Tutorials**: [Tutorials](https://youtube.com/ukc-tutorials)

## 🆘 Get Help

- **Community Discord**: [Join our server](https://discord.gg/ukc)
- **GitHub Issues**: [Report problems](https://github.com/your-repo/ukc/issues)
- **Email Support**: support@ultimatekitchencompendium.com
- **FAQ**: [Frequently Asked Questions](FAQ.md)

## ✅ Success Checklist

You're successfully running when you can:
- [ ] Access http://localhost:8000/health and see "healthy"
- [ ] Login with created user account
- [ ] Add an item to inventory
- [ ] Create a recipe
- [ ] Generate a shopping list
- [ ] Access API documentation at /docs
- [ ] Connect mobile apps and login

**Congratulations! You now have a fully functional kitchen management system. Happy cooking! 🍳**