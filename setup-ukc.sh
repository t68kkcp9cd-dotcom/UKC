#!/bin/bash
# Ultimate Kitchen Compendium Setup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="production"
INSTALL_PATH="/opt/ukc"
DB_PASSWORD=""
JWT_SECRET_KEY=""
SKIP_CHECKS=false

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check if running as root for system-wide install
    if [[ $EUID -ne 0 && "$INSTALL_PATH" == "/opt/ukc" ]]; then
        print_error "This script needs to be run as root for system-wide installation"
        print_info "Please run: sudo $0"
        exit 1
    fi
    
    # Check required commands
    local required_cmds=("docker" "docker-compose" "curl" "openssl")
    for cmd in "${required_cmds[@]}"; do
        if ! command -v $cmd &> /dev/null; then
            print_error "$cmd is required but not installed"
            exit 1
        fi
    done
    
    # Check Docker service
    if ! systemctl is-active --quiet docker; then
        print_error "Docker service is not running"
        print_info "Please start Docker: sudo systemctl start docker"
        exit 1
    fi
    
    print_success "All prerequisites met"
}

# Function to generate secure passwords
generate_password() {
    openssl rand -base64 32 | tr -d "\n"
}

# Function to generate secure keys
generate_key() {
    openssl rand -hex 32
}

# Function to create directory structure
create_directories() {
    print_info "Creating directory structure..."
    
    # Create main directory
    mkdir -p "$INSTALL_PATH"
    cd "$INSTALL_PATH"
    
    # Create subdirectories
    mkdir -p {backend,nginx,postgres,redis,ollama,logs,uploads,ssl,backup}
    mkdir -p backend/{app,docker,requirements,alembic}
    mkdir -p nginx/{conf.d,ssl}
    
    print_success "Directory structure created"
}

# Function to generate configuration files
generate_config() {
    print_info "Generating configuration files..."
    
    cd "$INSTALL_PATH"
    
    # Generate secrets if not provided
    if [[ -z "$DB_PASSWORD" ]]; then
        DB_PASSWORD=$(generate_password)
        print_info "Generated database password"
    fi
    
    if [[ -z "$JWT_SECRET_KEY" ]]; then
        JWT_SECRET_KEY=$(generate_key)
        print_info "Generated JWT secret key"
    fi
    
    # Create .env file
    cat > .env << EOF
# Ultimate Kitchen Compendium Configuration
# Generated on $(date)

# Database Configuration
DB_PASSWORD=$DB_PASSWORD
POSTGRES_USER=ukc
POSTGRES_DB=ukc_db

# JWT Configuration
JWT_SECRET_KEY=$JWT_SECRET_KEY
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=10080
JWT_REFRESH_EXPIRATION_DAYS=30

# Application Configuration
ENVIRONMENT=$ENVIRONMENT
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
    
    print_success "Configuration files generated"
}

# Function to setup Docker Compose
setup_docker_compose() {
    print_info "Setting up Docker Compose..."
    
    cd "$INSTALL_PATH"
    
    # Copy docker-compose.yml (assuming it's in the same directory as this script)
    if [[ -f "$(dirname "$0")/docker-compose.yml" ]]; then
        cp "$(dirname "$0")/docker-compose.yml" ./docker-compose.yml
    else
        print_warning "docker-compose.yml not found. Please copy it manually."
    fi
    
    # Create nginx configuration
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
    
    # Create PostgreSQL configuration for low-end hardware
    cat > postgres/postgresql.conf << 'EOF'
# PostgreSQL configuration optimized for low-end hardware
# Intel Xeon E5-2630 v3, 32GB RAM

# Memory Settings
shared_buffers = 8GB
effective_cache_size = 24GB
work_mem = 64MB
maintenance_work_mem = 2GB

# Connection Settings
max_connections = 100
listen_addresses = '*'
port = 5432

# Performance Settings
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200

# Logging
log_statement = 'none'
log_duration = off
log_lock_waits = on
log_error_verbosity = default

# Extensions
shared_preload_libraries = 'pg_stat_statements'
EOF
    
    print_success "Docker Compose setup completed"
}

# Function to pull Docker images
pull_images() {
    print_info "Pulling Docker images..."
    
    cd "$INSTALL_PATH"
    
    if [[ -f "docker-compose.yml" ]]; then
        docker-compose pull
        print_success "Docker images pulled"
    else
        print_warning "docker-compose.yml not found, skipping image pull"
    fi
}

# Function to setup SSL certificates
setup_ssl() {
    print_info "Setting up SSL certificates..."
    
    cd "$INSTALL_PATH"
    
    # Generate self-signed certificate for development
    if [[ "$ENVIRONMENT" == "development" ]]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ssl/selfsigned.key \
            -out ssl/selfsigned.crt \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        
        print_success "Self-signed SSL certificate generated"
    else
        print_info "Please configure your SSL certificates in the ssl/ directory"
    fi
}

# Function to create systemd service
create_systemd_service() {
    print_info "Creating systemd service..."
    
    cat > /etc/systemd/system/ukc.service << EOF
[Unit]
Description=Ultimate Kitchen Compendium
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$INSTALL_PATH
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd
    systemctl daemon-reload
    
    print_success "Systemd service created"
}

# Function to setup monitoring
setup_monitoring() {
    print_info "Setting up monitoring..."
    
    cd "$INSTALL_PATH"
    
    # Create monitoring directory
    mkdir -p monitoring/{prometheus,grafana}
    
    # Create Prometheus configuration
    cat > monitoring/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'ukc-app'
    static_configs:
      - targets: ['app:8000']
    metrics_path: /metrics
    
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
EOF
    
    print_success "Monitoring configuration created"
}

# Function to create backup script
create_backup_script() {
    print_info "Creating backup script..."
    
    cat > backup/backup.sh << 'EOF'
#!/bin/bash
# Ultimate Kitchen Compendium Backup Script

BACKUP_DIR="/opt/ukc/backup"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR/$DATE"

# Backup database
docker-compose exec -T db pg_dump -U ukc ukc_db > "$BACKUP_DIR/$DATE/database.sql"

# Backup uploads
tar -czf "$BACKUP_DIR/$DATE/uploads.tar.gz" -C /opt/ukc uploads/

# Backup configuration
cp /opt/ukc/.env "$BACKUP_DIR/$DATE/"

# Keep only last 7 days of backups
find "$BACKUP_DIR" -type d -name "20*" -mtime +7 -exec rm -rf {} \;

echo "Backup completed: $BACKUP_DIR/$DATE"
EOF
    
    chmod +x backup/backup.sh
    
    # Add to crontab
    (crontab -l 2>/dev/null || echo "") | grep -v "ukc/backup/backup.sh" | (cat; echo "0 2 * * * /opt/ukc/backup/backup.sh") | crontab -
    
    print_success "Backup script created and scheduled"
}

# Function to start services
start_services() {
    print_info "Starting services..."
    
    cd "$INSTALL_PATH"
    
    if [[ -f "docker-compose.yml" ]]; then
        docker-compose up -d
        
        # Wait for services to be ready
        print_info "Waiting for services to start..."
        sleep 30
        
        # Check if services are healthy
        if docker-compose ps | grep -q "Up (healthy)"; then
            print_success "Services started successfully"
        else
            print_warning "Some services may not be healthy. Check with: docker-compose ps"
        fi
        
        # Enable and start systemd service
        systemctl enable ukc
        systemctl start ukc
        
        print_success "Ultimate Kitchen Compendium is now running!"
        print_info "Backend API: http://localhost:8000"
        print_info "API Documentation: http://localhost:8000/docs"
        print_info ""
        print_info "To stop services: docker-compose down"
        print_info "To view logs: docker-compose logs -f"
        print_info "To backup: /opt/ukc/backup/backup.sh"
    else
        print_error "docker-compose.yml not found. Cannot start services."
    fi
}

# Function to show help
show_help() {
    cat << EOF
Ultimate Kitchen Compendium Setup Script

Usage: $0 [OPTIONS]

Options:
    -p, --path PATH         Installation path (default: /opt/ukc)
    -e, --environment ENV   Environment (development|production, default: production)
    --db-password PASS      Database password (auto-generated if not provided)
    --jwt-secret KEY        JWT secret key (auto-generated if not provided)
    --skip-checks           Skip prerequisite checks
    -h, --help              Show this help message

Examples:
    $0                      # Install with defaults
    $0 -p /home/user/ukc    # Install to custom path
    $0 -e development       # Install for development
    $0 --skip-checks        # Skip prerequisite checks

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--path)
            INSTALL_PATH="$2"
            shift 2
            ;;
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --db-password)
            DB_PASSWORD="$2"
            shift 2
            ;;
        --jwt-secret)
            JWT_SECRET_KEY="$2"
            shift 2
            ;;
        --skip-checks)
            SKIP_CHECKS=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main installation process
main() {
    print_info "Starting Ultimate Kitchen Compendium installation..."
    print_info "Installation path: $INSTALL_PATH"
    print_info "Environment: $ENVIRONMENT"
    
    # Check prerequisites unless skipped
    if [[ "$SKIP_CHECKS" == false ]]; then
        check_prerequisites
    fi
    
    # Create directories
    create_directories
    
    # Generate configuration
    generate_config
    
    # Setup Docker Compose
    setup_docker_compose
    
    # Pull images
    pull_images
    
    # Setup SSL
    setup_ssl
    
    # Create systemd service
    create_systemd_service
    
    # Setup monitoring
    setup_monitoring
    
    # Create backup script
    create_backup_script
    
    # Start services
    start_services
    
    print_success "Installation completed successfully!"
    print_info "Your Ultimate Kitchen Compendium is ready to use."
}

# Run main function
main "$@"