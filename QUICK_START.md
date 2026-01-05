# Ultimate Kitchen Compendium - Quick Start Guide

Get your kitchen management system up and running in under 10 minutes!

## ⚡ Fast Track Installation

### Option 1: One-Command Setup (Recommended)
```bash
# Run the automated setup script
curl -fsSL https://raw.githubusercontent.com/your-repo/ukc/main/setup-ukc.sh | sudo bash
```

### Option 2: Quick Docker Setup
```bash
# Create directory
mkdir -p ~/ukc && cd ~/ukc

# Download docker-compose.yml
curl -O https://raw.githubusercontent.com/your-repo/ukc/main/docker-compose.yml

# Create minimal .env file
cat > .env << EOF
DB_PASSWORD=$(openssl rand -base64 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
ENVIRONMENT=production
EOF

# Start services
docker-compose up -d
```

### Option 3: Proxmox VE LXC
```bash
# Create LXC container (run on Proxmox host)
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
pct enter 1001

# Inside container, run the setup script
curl -fsSL https://raw.githubusercontent.com/your-repo/ukc/main/setup-ukc.sh | bash
```

## 🎯 First Steps After Installation

### 1. Verify Installation (2 minutes)
```bash
# Check if services are running
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

### 3. Access API Documentation (1 minute)
Open your browser and navigate to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 4. Create First User (2 minutes)
```bash
# Use the interactive API docs or run this curl command
curl -X POST "http://localhost:8000/api/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d '{
        "username": "admin",
        "email": "admin@example.com",
        "password": "your-secure-password"
    }'
```

## 📱 Connect Mobile Apps

### iOS Setup
1. Download from App Store
2. Open app and go to Settings
3. Enter API endpoint: `http://your-server-ip:8000`
4. Login with created credentials

### Android Setup
1. Download from Google Play Store
2. Open app and go to Settings
3. Enter API endpoint: `http://your-server-ip:8000`
4. Login with created credentials

## 🚀 Essential First Actions

### 1. Add Your First Item
```bash
# Using the API
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
        "title": "Tomato Salad",
        "description": "Fresh and simple tomato salad",
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

## ⚙️ Configuration

### Basic Configuration
Edit the `.env` file to customize:

```bash
# Application settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Security
JWT_EXPIRATION_MINUTES=10080  # 7 days

# Features
ENABLE_AI_FEATURES=true
ENABLE_GAMIFICATION=true
```

### Advanced Configuration
See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for advanced configuration options.

## 🔍 Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs app

# Common issues:
# 1. Port 8000 already in use
# 2. Database connection failed
# 3. Insufficient memory

# Solutions:
# 1. Change port in docker-compose.yml
# 2. Check database container: docker-compose logs db
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

# Test AI endpoint
curl http://localhost:11434/api/tags
```

### Mobile App Connection Issues
```bash
# Check network connectivity
ping your-server-ip

# Check firewall
sudo ufw status

# Allow port 8000
sudo ufw allow 8000

# Check API endpoint
curl http://your-server-ip:8000/health
```

## 📊 Monitoring

### Basic Monitoring
```bash
# Check service status
docker-compose ps

# View real-time logs
docker-compose logs -f

# Check resource usage
docker stats
```

### Health Checks
```bash
# Application health
curl http://localhost:8000/health

# Database health
docker-compose exec db pg_isready -U ukc

# Redis health
docker-compose exec redis redis-cli ping
```

## 🔧 Useful Commands

### Daily Operations
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f app

# Update images
docker-compose pull
docker-compose up -d
```

### Backup
```bash
# Quick backup
docker-compose exec db pg_dump -U ukc ukc_db > backup.sql

# Restore
docker-compose exec -T db psql -U ukc ukc_db < backup.sql
```

### Performance
```bash
# Monitor resources
docker stats

# Clean up
docker system prune -f

# Reset everything (WARNING: Data loss)
docker-compose down -v
docker-compose up -d
```

## 🎉 Next Steps

### Explore Features
1. **Inventory Management**: Add more items, set expiration dates
2. **Recipe Collection**: Import recipes from websites
3. **Meal Planning**: Create weekly meal plans
4. **Shopping Lists**: Generate from meal plans
5. **AI Assistance**: Get recipe suggestions and adaptations

### Customize Your Experience
1. **User Profile**: Set dietary preferences and allergens
2. **Household Settings**: Add family members
3. **Theme**: Switch between light and dark modes
4. **Notifications**: Configure alerts and reminders

### Advanced Features
1. **Store Integration**: Connect to local grocery stores
2. **Smart Devices**: Integrate with kitchen scales
3. **Voice Commands**: Use voice-guided cooking
4. **Analytics**: View consumption patterns and waste reduction

## 📚 Learn More

- **Detailed Deployment**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **API Documentation**: http://localhost:8000/docs
- **Mobile App Setup**: [mobile/README.md](mobile/)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

## 🆘 Get Help

- **Issues**: GitHub Issues
- **Discord**: Community chat
- **Email**: support@ultimatekitchencompendium.com
- **Documentation**: Full docs at docs.ultimatekitchencompendium.com

---

**Congratulations! You now have a fully functional kitchen management system. Happy cooking! 🍳**