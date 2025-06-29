# Catalyst Trading System - Implementation Instructions
**Option 1: Premium Single Droplet + Managed Database ($96 AUD/month)**

## 🎯 **PROJECT OVERVIEW**

Build a complete news-driven algorithmic trading system with the following architecture:
- **Single Premium DigitalOcean Droplet** (8GB RAM, 4 vCPUs, $72/month)
- **Managed PostgreSQL Database** (2GB RAM, automated backups, $24/month)
- **8 Microservices** running in Docker containers
- **Total Budget**: $96 AUD/month

## 🏗️ **SYSTEM ARCHITECTURE**

### Core Services (8 total):
1. **Coordination Service** (Port 5000) - Orchestrates trading workflow
2. **News Collection Service** (Port 5008) - Gathers market intelligence 24/7
3. **Security Scanner Service** (Port 5001) - Selects catalyst-driven trading candidates
4. **Pattern Analysis Service** (Port 5002) - Detects technical patterns with news context
5. **Technical Analysis Service** (Port 5003) - Generates buy/sell signals
6. **Paper Trading Service** (Port 5005) - Executes trades via Alpaca API
7. **Reporting Service** (Port 5009) - Performance analytics and metrics
8. **Web Dashboard Service** (Port 5010) - Real-time monitoring interface

### Supporting Components:
- **Redis Cache** (Port 6379) - Fast data access and session management
- **Nginx Reverse Proxy** (Ports 80/443) - Load balancing and SSL termination
- **Prometheus Monitoring** (Port 9090) - System metrics and health monitoring

## 📁 **REQUIRED FILES TO CREATE**

### 1. Container Orchestration:
- **`docker-compose.yml`** - Main deployment configuration with memory limits and resource allocation
- **`.env.example`** - Environment variable template for managed database setup

### 2. Docker Configurations (8 files):
- **`Dockerfile.coordination`** - Coordination service container
- **`Dockerfile.news`** - News collection service container  
- **`Dockerfile.scanner`** - Security scanner service container
- **`Dockerfile.patterns`** - Pattern analysis service container (includes TA-Lib)
- **`Dockerfile.technical`** - Technical analysis service container (includes TA-Lib)
- **`Dockerfile.trading`** - Paper trading service container
- **`Dockerfile.reporting`** - Reporting service container
- **`Dockerfile.dashboard`** - Web dashboard service container

### 3. Configuration Files:
- **`requirements.txt`** - Complete Python dependencies for all services
- **`nginx.conf`** - Reverse proxy configuration with SSL support
- **`prometheus.yml`** - Monitoring configuration
- **`init_database.sql`** - PostgreSQL schema optimized for DigitalOcean

## 🔧 **TECHNICAL SPECIFICATIONS**

### Database Configuration:
- **Engine**: PostgreSQL 14
- **Connection**: DigitalOcean managed database with SSL
- **Schema**: Complete trading system with news, patterns, signals, trades tables
- **Backup**: Automated daily backups via DigitalOcean

### Service Resource Allocation:
- **Scanner/Pattern/Technical Services**: 1GB RAM each (heavy processing)
- **Dashboard**: 1GB RAM (web interface)
- **Coordination/News/Trading/Reporting**: 512MB RAM each
- **Redis**: 1GB RAM with LRU eviction policy
- **Nginx**: 256MB RAM
- **Prometheus**: 512MB RAM

### Python Dependencies:
- **Core**: Flask, gunicorn, psycopg2-binary, redis
- **Data**: pandas, numpy, scipy
- **Trading**: yfinance, TA-Lib, alpaca-trade-api
- **News**: requests, feedparser, python-textblob
- **Utilities**: python-dotenv, structlog, prometheus-client

## 🌐 **NETWORK CONFIGURATION**

### Port Mapping:
- **80/443**: Nginx (public web access)
- **5000**: Coordination API
- **5001**: Scanner API  
- **5002**: Pattern Analysis API
- **5003**: Technical Analysis API
- **5005**: Trading API
- **5008**: News Collection API
- **5009**: Reporting API
- **5010**: Web Dashboard
- **6379**: Redis Cache
- **9090**: Prometheus Metrics

### Service Discovery:
- Internal Docker network communication
- Services reference each other by container name
- Environment variables for external database connection

## 🔐 **SECURITY REQUIREMENTS**

### Environment Variables:
- **DATABASE_URL**: Managed PostgreSQL connection string with SSL
- **NEWSAPI_KEY**: News API access key
- **ALPHAVANTAGE_KEY**: Financial data API key  
- **ALPACA_API_KEY**: Paper trading API key
- **ALPACA_SECRET_KEY**: Paper trading secret key
- **Various trading parameters**: position sizes, stop losses, etc.

### Container Security:
- Non-root user in all containers
- Minimal base images (python:3.10-slim)
- Health checks for all services
- Resource limits to prevent resource exhaustion

## 📊 **DEPLOYMENT CONFIGURATION**

### Docker Compose Features:
- **Resource limits**: Memory constraints for each service
- **Health checks**: Automated service monitoring
- **Restart policies**: Auto-recovery from failures
- **Volume persistence**: Redis and Prometheus data retention
- **Dependency management**: Proper service startup order

### Repository Structure:
```
catalyst-trading-system/
├── docker-compose.yml
├── .env.example
├── requirements.txt
├── nginx.conf
├── prometheus.yml
├── init_database.sql
├── Dockerfile.coordination
├── Dockerfile.news
├── Dockerfile.scanner
├── Dockerfile.patterns
├── Dockerfile.technical
├── Dockerfile.trading
├── Dockerfile.reporting
├── Dockerfile.dashboard
└── README.md
```

## 🚀 **IMPLEMENTATION REQUIREMENTS**

### Docker Compose Configuration:
- Use version '3.8' for compatibility
- Include resource limits (deploy.resources.limits.memory)
- Configure proper service dependencies
- Set restart policies to "unless-stopped"
- Map all required ports
- Include health checks with curl commands

### Dockerfile Requirements:
- Start with python:3.10-slim base image
- Install system dependencies (gcc, postgresql-client, curl)
- For pattern/technical services: Include TA-Lib C library installation
- Copy requirements.txt and install Python dependencies
- Create non-root trading user for security
- Set proper environment variables (PORT, SERVICE_NAME, PYTHONPATH)
- Include health check using curl to /health endpoint
- Expose appropriate port for each service

### Special Considerations:
- **TA-Lib Installation**: Pattern and Technical services need full TA-Lib C library build process
- **Database Connection**: Use managed PostgreSQL URL from environment
- **Redis Configuration**: Include memory limits and LRU eviction
- **Nginx Config**: Route traffic to appropriate services based on path
- **Monitoring**: Include Prometheus for system metrics

## 📋 **GITHUB REPOSITORY**

### Repository Details:
- **Username**: tradingsystem
- **Repository Name**: catalyst-trading-system
- **Branch**: main
- **Visibility**: Public (for DigitalOcean deployment)

### File Organization:
- All Docker and configuration files in repository root
- Clear README.md with deployment instructions
- .env.example with all required environment variables
- Complete PostgreSQL schema for fresh deployment

## 🎯 **SUCCESS CRITERIA**

The implementation should result in:
1. **Complete deployment files** ready for DigitalOcean droplet
2. **All 8 services** containerized and configured
3. **Resource-optimized** setup for 8GB RAM droplet
4. **Professional monitoring** with Prometheus and health checks
5. **Secure configuration** with SSL and non-root containers
6. **Managed database integration** with DigitalOcean PostgreSQL
7. **Under $100 AUD budget** ($96/month total cost)

## 📞 **HANDOFF NOTES**

This system implements a complete news-driven algorithmic trading platform optimized for a $100 AUD monthly budget. The architecture prioritizes cost-effectiveness while maintaining professional-grade capabilities including monitoring, security, and scalability.

The deployment uses a single premium DigitalOcean droplet with managed database to achieve maximum value within budget constraints while providing a foundation for future scaling as trading profits increase.
