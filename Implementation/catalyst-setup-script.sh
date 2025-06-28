#!/bin/bash
# Catalyst Trading System - DigitalOcean Setup Script
# Budget Infrastructure: ~$40 USD/month
# Project: Catalyst-Trading-System

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Catalyst Trading System - Infrastructure Setup${NC}"
echo -e "${GREEN}=========================================${NC}"

# Configuration
PROJECT_NAME="Catalyst-Trading-System"
DROPLET_NAME="catalyst-trading-prod"
REGION="sgp1"
DROPLET_SIZE="s-2vcpu-4gb"
SPACES_BUCKET="catalyst-trading-backups"

# Generate secure passwords
echo -e "\n${YELLOW}Generating secure passwords...${NC}"
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
ADMIN_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

# Save passwords to secure file
cat > catalyst-credentials.txt << EOF
# Catalyst Trading System Credentials
# Generated: $(date)
# KEEP THIS FILE SECURE!

PostgreSQL Password: ${DB_PASSWORD}
Redis Password: ${REDIS_PASSWORD}
Admin Password: ${ADMIN_PASSWORD}
EOF

chmod 600 catalyst-credentials.txt
echo -e "${GREEN}✓ Passwords saved to catalyst-credentials.txt${NC}"

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo -e "${RED}doctl CLI not found. Please install it first:${NC}"
    echo "brew install doctl (macOS)"
    echo "or visit: https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Check authentication
echo -e "\n${YELLOW}Checking DigitalOcean authentication...${NC}"
if ! doctl account get &> /dev/null; then
    echo -e "${RED}Not authenticated. Running: doctl auth init${NC}"
    doctl auth init
fi

# Create project
echo -e "\n${YELLOW}Creating project: ${PROJECT_NAME}${NC}"
if doctl projects list --format Name --no-header | grep -q "^${PROJECT_NAME}$"; then
    echo -e "${GREEN}✓ Project already exists${NC}"
    PROJECT_ID=$(doctl projects list --format Name,ID --no-header | grep "^${PROJECT_NAME}" | awk '{print $2}')
else
    PROJECT_OUTPUT=$(doctl projects create \
        --name "${PROJECT_NAME}" \
        --description "News-driven algorithmic trading system" \
        --purpose "Trading and financial services" \
        --format ID --no-header)
    PROJECT_ID=$PROJECT_OUTPUT
    echo -e "${GREEN}✓ Project created: ${PROJECT_ID}${NC}"
fi

# Get SSH key
echo -e "\n${YELLOW}Checking SSH keys...${NC}"
SSH_KEYS=$(doctl compute ssh-key list --format ID --no-header)
if [ -z "$SSH_KEYS" ]; then
    echo -e "${RED}No SSH keys found. Please add one:${NC}"
    echo "doctl compute ssh-key import my-key --public-key-file ~/.ssh/id_rsa.pub"
    exit 1
fi
SSH_KEY_ID=$(echo $SSH_KEYS | awk '{print $1}')
echo -e "${GREEN}✓ Using SSH key: ${SSH_KEY_ID}${NC}"

# Create Spaces bucket for backups
echo -e "\n${YELLOW}Creating Spaces bucket for backups...${NC}"
# Note: Spaces creation requires s3cmd or DO console
echo -e "${YELLOW}Please create Spaces bucket manually in DO console:${NC}"
echo "  Name: ${SPACES_BUCKET}-${REGION}"
echo "  Region: ${REGION}"
echo "  Press Enter when created..."
read -r

# Create Droplet
echo -e "\n${YELLOW}Creating Droplet: ${DROPLET_NAME}${NC}"
if doctl compute droplet list --format Name --no-header | grep -q "^${DROPLET_NAME}$"; then
    echo -e "${YELLOW}Droplet already exists${NC}"
    DROPLET_ID=$(doctl compute droplet list --format Name,ID --no-header | grep "^${DROPLET_NAME}" | awk '{print $2}')
    DROPLET_IP=$(doctl compute droplet get $DROPLET_ID --format PublicIPv4 --no-header)
else
    DROPLET_OUTPUT=$(doctl compute droplet create ${DROPLET_NAME} \
        --image docker-20-04 \
        --size ${DROPLET_SIZE} \
        --region ${REGION} \
        --ssh-keys ${SSH_KEY_ID} \
        --tag-names production,trading,catalyst \
        --wait \
        --format ID,PublicIPv4 --no-header)
    
    DROPLET_ID=$(echo $DROPLET_OUTPUT | awk '{print $1}')
    DROPLET_IP=$(echo $DROPLET_OUTPUT | awk '{print $2}')
    echo -e "${GREEN}✓ Droplet created: ${DROPLET_ID} (${DROPLET_IP})${NC}"
fi

# Assign to project
echo -e "\n${YELLOW}Assigning resources to project...${NC}"
doctl projects resources assign ${PROJECT_ID} --resource=droplet:${DROPLET_ID} || true

# Create floating IP
echo -e "\n${YELLOW}Creating floating IP...${NC}"
FLOATING_IPS=$(doctl compute floating-ip list --format IP --no-header)
if [ -z "$FLOATING_IPS" ]; then
    FLOATING_IP=$(doctl compute floating-ip create --region ${REGION} --format IP --no-header)
    echo -e "${GREEN}✓ Floating IP created: ${FLOATING_IP}${NC}"
    
    # Assign to droplet
    doctl compute floating-ip-action assign ${FLOATING_IP} ${DROPLET_ID}
    echo -e "${GREEN}✓ Floating IP assigned to droplet${NC}"
else
    FLOATING_IP=$(echo $FLOATING_IPS | awk '{print $1}')
    echo -e "${GREEN}✓ Using existing floating IP: ${FLOATING_IP}${NC}"
fi

# Wait for droplet to be ready
echo -e "\n${YELLOW}Waiting for droplet to be ready...${NC}"
sleep 30

# Create setup script for the droplet
cat > droplet-setup.sh << 'DROPLET_SCRIPT'
#!/bin/bash
set -e

echo "Starting Catalyst Trading System setup..."

# Update system
apt update && apt upgrade -y

# Install required packages
apt install -y curl git htop iotop nethogs postgresql-client redis-tools

# Install Docker
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Create trading user
if ! id -u trading &> /dev/null; then
    useradd -m -s /bin/bash trading
    usermod -aG docker trading
fi

# Setup directories
mkdir -p /opt/catalyst-trading/{data,logs,config,backups,services}
mkdir -p /opt/catalyst-trading/data/{postgres,redis}
chown -R trading:trading /opt/catalyst-trading

# Setup swap (important for 4GB RAM)
if [ ! -f /swapfile ]; then
    fallocate -l 4G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

# Configure firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Install s3cmd for Spaces backups
apt install -y python3-pip
pip3 install s3cmd

echo "Droplet setup complete!"
DROPLET_SCRIPT

# Copy and run setup script
echo -e "\n${YELLOW}Configuring droplet...${NC}"
scp -o StrictHostKeyChecking=no droplet-setup.sh root@${DROPLET_IP}:/tmp/
ssh -o StrictHostKeyChecking=no root@${DROPLET_IP} "chmod +x /tmp/droplet-setup.sh && /tmp/droplet-setup.sh"

# Create Docker Compose file
cat > docker-compose.yml << EOF
version: '3.8'

networks:
  catalyst-net:
    driver: bridge

services:
  postgres:
    image: postgres:14-alpine
    container_name: catalyst-postgres
    restart: always
    networks:
      - catalyst-net
    volumes:
      - /opt/catalyst-trading/data/postgres:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: trading_system
      POSTGRES_USER: trading_app
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_INITDB_ARGS: "-E UTF8"
    ports:
      - "127.0.0.1:5432:5432"
    deploy:
      resources:
        limits:
          memory: 512M
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U trading_app"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:6-alpine
    container_name: catalyst-redis
    restart: always
    networks:
      - catalyst-net
    volumes:
      - /opt/catalyst-trading/data/redis:/data
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    ports:
      - "127.0.0.1:6379:6379"
    deploy:
      resources:
        limits:
          memory: 256M
    healthcheck:
      test: ["CMD", "redis-cli", "--pass", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Trading services will be added here
  # coordination:
  #   build: ./services/coordination
  #   ... etc

EOF

# Create environment file
cat > .env << EOF
# Catalyst Trading System Environment
PROJECT_NAME=Catalyst-Trading-System
ENVIRONMENT=production

# Database
DB_PASSWORD=${DB_PASSWORD}
DATABASE_URL=postgresql://trading_app:${DB_PASSWORD}@postgres:5432/trading_system

# Redis
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379

# Admin
ADMIN_PASSWORD=${ADMIN_PASSWORD}

# Services
COORDINATION_PORT=5000
SCANNER_PORT=5001
PATTERN_PORT=5002
TECHNICAL_PORT=5003
PAPER_TRADING_PORT=5005
NEWS_PORT=5008
REPORTING_PORT=5009
DASHBOARD_PORT=5010
EOF

# Copy files to droplet
echo -e "\n${YELLOW}Deploying configuration...${NC}"
scp docker-compose.yml root@${DROPLET_IP}:/opt/catalyst-trading/
scp .env root@${DROPLET_IP}:/opt/catalyst-trading/

# Create backup script
cat > backup.sh << 'BACKUP_SCRIPT'
#!/bin/bash
# Catalyst Trading System Backup Script

BACKUP_DIR="/opt/catalyst-trading/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup PostgreSQL
docker exec catalyst-postgres pg_dump -U trading_app trading_system | gzip > ${BACKUP_DIR}/postgres_${TIMESTAMP}.sql.gz

# Backup Redis
docker exec catalyst-redis redis-cli --pass ${REDIS_PASSWORD} BGSAVE
sleep 5
cp /opt/catalyst-trading/data/redis/dump.rdb ${BACKUP_DIR}/redis_${TIMESTAMP}.rdb

# Upload to Spaces (configure s3cmd first)
# s3cmd put ${BACKUP_DIR}/*_${TIMESTAMP}.* s3://catalyst-trading-backups-sgp1/

# Clean old local backups (keep 7 days)
find ${BACKUP_DIR} -type f -mtime +7 -delete
BACKUP_SCRIPT

scp backup.sh root@${DROPLET_IP}:/opt/catalyst-trading/
ssh root@${DROPLET_IP} "chmod +x /opt/catalyst-trading/backup.sh"

# Create monitoring script
cat > monitor.sh << 'MONITOR_SCRIPT'
#!/bin/bash
echo "=== Catalyst Trading System Monitor ==="
echo "Time: $(date)"
echo ""
echo "=== System Resources ==="
free -h
echo ""
echo "=== Docker Containers ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "=== Docker Stats ==="
docker stats --no-stream
echo ""
echo "=== Disk Usage ==="
df -h | grep -E '^/dev/|^Filesystem'
MONITOR_SCRIPT

scp monitor.sh root@${DROPLET_IP}:/opt/catalyst-trading/
ssh root@${DROPLET_IP} "chmod +x /opt/catalyst-trading/monitor.sh"

# Start services
echo -e "\n${YELLOW}Starting services...${NC}"
ssh root@${DROPLET_IP} "cd /opt/catalyst-trading && docker-compose up -d postgres redis"

# Final output
echo -e "\n${GREEN}=========================================${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "${YELLOW}Access Information:${NC}"
echo "Droplet IP: ${DROPLET_IP}"
echo "Floating IP: ${FLOATING_IP}"
echo "SSH: ssh root@${FLOATING_IP}"
echo ""
echo -e "${YELLOW}Credentials saved to:${NC} catalyst-credentials.txt"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. SSH to droplet: ssh root@${FLOATING_IP}"
echo "2. Check services: cd /opt/catalyst-trading && docker-compose ps"
echo "3. View logs: docker-compose logs -f"
echo "4. Run monitor: /opt/catalyst-trading/monitor.sh"
echo ""
echo -e "${YELLOW}Configure Spaces backup:${NC}"
echo "1. s3cmd --configure"
echo "2. Use DigitalOcean Spaces keys"
echo "3. Set endpoint: sgp1.digitaloceanspaces.com"
echo ""
echo -e "${GREEN}Ready for Phase 2: Containerization!${NC}"

# Clean up local files
rm -f droplet-setup.sh docker-compose.yml .env backup.sh monitor.sh