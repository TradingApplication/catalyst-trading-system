# Trading Application Migration Plan: GitHub Codespaces → DigitalOcean

**Migration Plan Version**: 1.0.0  
**Date**: June 24, 2025  
**Target Environment**: DigitalOcean Production Infrastructure (Singapore Region)  

## Executive Summary

This plan outlines the migration of the Trading Application from GitHub Codespaces development environment to a production-ready DigitalOcean infrastructure in Singapore (closest region to Western Australia). The migration includes infrastructure setup, service containerization, database migration, security implementation, and CI/CD pipeline establishment.

**Important**: This system is currently **rule-based, not ML-based**. While ML infrastructure exists as placeholders, the core trading logic uses manual pattern detection and fixed algorithms. The migration plan includes provisions for future ML development as outlined in the ML Analysis Roadmap.

### Current State Analysis
- **Platform**: GitHub Codespaces (development environment)
- **Architecture**: 8 REST API microservices + hybrid manager (rule-based system)
- **Database**: SQLite with WAL mode
- **Storage**: Workspace persistent storage (`/workspaces/trading-system/`)
- **Networking**: localhost ports 5000-5010
- **Deployment**: Manual startup scripts (`start_trading.sh`, `hybrid_manager.py`)
- **ML Status**: Placeholder code only - no trained models or ML logic

### Target State Goals
- **Platform**: DigitalOcean production infrastructure (Singapore region)
- **Architecture**: Containerized rule-based microservices with orchestration
- **Database**: PostgreSQL with high availability
- **Storage**: Persistent volumes with backups
- **Networking**: Load-balanced with SSL termination
- **Deployment**: Automated CI/CD pipeline
- **ML Readiness**: Infrastructure prepared for future ML development per roadmap

---

## Table of Contents

1. [Migration Overview](#1-migration-overview)
2. [Infrastructure Architecture](#2-infrastructure-architecture)
3. [Phase 1: Infrastructure Setup](#3-phase-1-infrastructure-setup)
4. [Phase 2: Application Containerization](#4-phase-2-application-containerization)
5. [Phase 3: Database Migration](#5-phase-3-database-migration)
6. [Phase 4: Service Deployment](#6-phase-4-service-deployment)
7. [Phase 5: Security & Monitoring](#7-phase-5-security--monitoring)
8. [Phase 6: CI/CD Pipeline](#8-phase-6-cicd-pipeline)
9. [Testing & Validation](#9-testing--validation)
10. [Rollback Plan](#10-rollback-plan)
11. [Timeline & Resources](#11-timeline--resources)

---

## 1. Migration Overview

### 1.1 Migration Strategy
**Approach**: Blue-Green deployment with parallel environment setup

**Key Principles**:
- Zero-downtime migration capability
- Gradual service migration with fallback options
- Data integrity throughout migration process
- Comprehensive testing at each phase

### 1.2 Service Mapping

| Current Service | Port | Purpose | Container Name | Critical | Implementation |
|----------------|------|---------|----------------|----------|----------------|
| Coordination Service | 5000 | Workflow orchestration | trading-coordinator | Yes | Rule-based trading cycle management |
| Security Scanner | 5001 | Market scanning | trading-scanner | Yes | Rule-based security selection |
| Pattern Analysis | 5002 | Technical patterns | trading-patterns | Yes | Manual pattern detection algorithms |
| Technical Analysis | 5003 | Indicators & signals | trading-technical | Yes | Rule-based signal generation |
| Paper Trading | 5005 | Trade execution | trading-execution | Yes | Alpaca API integration |
| Pattern Recognition | 5006 | Advanced patterns | trading-pattern-rec | No | Manual pattern algorithms |
| News Service | 5008 | Sentiment analysis | trading-news | No | TextBlob + keyword sentiment |
| Reporting Service | 5009 | Analytics & reports | trading-reports | No | Database analytics |
| Web Dashboard | 5010 | User interface | trading-dashboard | Yes | Flask web interface |
| Hybrid Manager | N/A | Service orchestration | trading-manager | Yes | Process management |
| Database | SQLite | Data persistence | PostgreSQL | Yes | Managed database service |

### 1.3 Infrastructure Components

**Core Infrastructure** (Singapore Region):
- DigitalOcean App Platform (for microservices deployment)
- DigitalOcean Managed PostgreSQL (database with backup)
- DigitalOcean Spaces (file storage and backups)
- DigitalOcean Load Balancer (SSL termination)
- DigitalOcean VPC (network isolation)

**Supporting Services**:
- Redis (caching and session management)
- DigitalOcean Monitoring (metrics and alerts)
- DigitalOcean Container Registry (image storage)
- GitHub Actions (CI/CD pipeline)

**Future ML Infrastructure** (prepared but not implemented):
- Additional compute resources for model training
- Object storage for training data and model artifacts
- Container registry for ML model serving
- Monitoring for model performance and drift detection

---

## 2. Infrastructure Architecture

### 2.1 Target Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    DigitalOcean Production Environment           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐        ┌──────────────────────────────┐   │
│  │ Load Balancer   │────────▶│    SSL Termination          │   │
│  │ (DO LB)         │        │    (Let's Encrypt)           │   │
│  └─────────────────┘        └──────────────┬───────────────┘   │
│                                           │                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              App Platform Cluster                      │   │
│  │                                                         │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │   │
│  │  │Coordinator│ │ Scanner  │ │Patterns  │ │Technical │   │   │
│  │  │(Container)│ │(Container)│ │(Container)│ │(Container)│   │   │
│  │  └─────┬────┘ └─────┬────┘ └─────┬────┘ └─────┬────┘   │   │
│  │        │            │            │            │        │   │
│  │  ┌─────▼────┐ ┌─────▼────┐ ┌─────▼────┐ ┌─────▼────┐   │   │
│  │  │Execution │ │Pattern   │ │   News   │ │ Reports  │   │   │
│  │  │(Container)│ │Recognition│ │(Container)│ │(Container)│   │   │
│  │  └─────┬────┘ └─────┬────┘ └─────┬────┘ └─────┬────┘   │   │
│  │        │            │            │            │        │   │
│  │  ┌─────▼──────────────────────────────────────▼────┐   │   │
│  │  │           Web Dashboard (Container)             │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                External Services                        │   │
│  │                                                         │   │
│  │  ┌──────────────┐  ┌─────────────┐  ┌─────────────┐   │   │
│  │  │ PostgreSQL   │  │   Redis     │  │ DO Spaces   │   │   │
│  │  │ (Managed DB) │  │ (Cache)     │  │ (Storage)   │   │   │
│  │  └──────────────┘  └─────────────┘  └─────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                Monitoring & Logging                     │   │
│  │                                                         │   │
│  │  ┌──────────────┐  ┌─────────────┐  ┌─────────────┐   │   │
│  │  │ DO Monitoring│  │ Log Alerts  │  │ Uptime      │   │   │
│  │  │              │  │             │  │ Monitoring  │   │   │
│  │  └──────────────┘  └─────────────┘  └─────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Network Architecture

**VPC Configuration** (Singapore Region):
- **VPC CIDR**: 10.0.0.0/16
- **Public Subnet**: 10.0.1.0/24 (Load Balancer)
- **Private Subnet**: 10.0.2.0/24 (App Platform)
- **Database Subnet**: 10.0.3.0/24 (PostgreSQL)

**Security Groups**:
- **Load Balancer**: HTTP (80), HTTPS (443) from 0.0.0.0/0
- **App Platform**: Internal communication only, health checks
- **Database**: PostgreSQL (5432) from App Platform only
- **Redis**: Redis (6379) from App Platform only

**Latency Considerations for Western Australia**:
- Singapore region provides ~40-60ms latency to Perth
- Optimal for real-time trading data requirements
- CDN integration for static assets if needed

---

## 3. Phase 1: Infrastructure Setup

### 3.1 DigitalOcean Account Setup

**Prerequisites**:
- DigitalOcean account with billing configured
- Domain name for SSL certificates
- GitHub repository access for CI/CD

**Initial Setup Steps**:

1. **Create DigitalOcean Project**
```bash
# Using doctl CLI
doctl projects create \
  --name "Trading Application" \
  --description "Production trading system infrastructure" \
  --purpose "Trading and financial services"
```

2. **Setup VPC Network**
```bash
# Create VPC in Singapore
doctl vpcs create \
  --name trading-vpc \
  --region sgp1 \
  --ip-range 10.0.0.0/16
```

3. **Create Container Registry**
```bash
# Create private registry
doctl registry create trading-registry
```

### 3.2 Domain and SSL Setup

**Domain Configuration**:
```bash
# Add domain to DigitalOcean
doctl domains create trading-app.yourdomain.com

# Setup DNS records
doctl domains records create trading-app.yourdomain.com \
  --type A \
  --name @ \
  --data [LOAD_BALANCER_IP]

doctl domains records create trading-app.yourdomain.com \
  --type CNAME \
  --name api \
  --data trading-app.yourdomain.com
```

### 3.3 Database Setup

**PostgreSQL Managed Database**:
```bash
# Create PostgreSQL cluster in Singapore
doctl databases create trading-db \
  --engine postgres \
  --version 14 \
  --region sgp1 \
  --size db-s-2vcpu-4gb \
  --num-nodes 2 \
  --vpc-uuid [VPC_UUID]
```

**Database Configuration**:
```sql
-- Create application database and user
CREATE DATABASE trading_system;
CREATE USER trading_app WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE trading_system TO trading_app;

-- Enable required extensions
\c trading_system;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
```

### 3.4 Redis Setup

**Redis Cache Configuration**:
```bash
# Create Redis cluster in Singapore
doctl databases create trading-redis \
  --engine redis \
  --version 6 \
  --region sgp1 \
  --size db-s-1vcpu-1gb \
  --num-nodes 1 \
  --vpc-uuid [VPC_UUID]
```

---

## 4. Phase 2: Application Containerization

### 4.1 Dockerfile Creation

**Base Dockerfile Template**:
```dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN groupadd -r trading && useradd -r -g trading trading
RUN chown -R trading:trading /app
USER trading

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

# Start command
CMD ["python", "app.py"]
```

### 4.2 Service-Specific Dockerfiles

**Coordination Service Dockerfile**:
```dockerfile
FROM python:3.10-slim as base

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY coordination_service.py .
COPY database_utils.py .
COPY trading_config.py .

# Environment variables
ENV PORT=5000
ENV SERVICE_NAME=coordination

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

EXPOSE 5000

CMD ["python", "coordination_service.py"]
```

### 4.3 Docker Compose for Local Testing

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: trading_system
      POSTGRES_USER: trading_app
      POSTGRES_PASSWORD: local_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

  coordination-service:
    build:
      context: .
      dockerfile: Dockerfile.coordination
    environment:
      - DATABASE_URL=postgresql://trading_app:local_password@postgres:5432/trading_system
      - REDIS_URL=redis://redis:6379
    ports:
      - "5000:5000"
    depends_on:
      - postgres
      - redis

  scanner-service:
    build:
      context: .
      dockerfile: Dockerfile.scanner
    environment:
      - DATABASE_URL=postgresql://trading_app:local_password@postgres:5432/trading_system
      - COORDINATION_URL=http://coordination-service:5000
    ports:
      - "5001:5001"
    depends_on:
      - postgres
      - coordination-service

  # Additional services...

volumes:
  postgres_data:
```

### 4.4 Environment Configuration

**Environment Variables Template**:
```env
# Database Configuration
DATABASE_URL=postgresql://username:password@host:5432/database
REDIS_URL=redis://host:6379

# Service Configuration
COORDINATION_SERVICE_URL=http://coordination-service:5000
SERVICE_PORT=5000
SERVICE_NAME=coordination

# Trading API Configuration
ALPACA_API_KEY=your_api_key
ALPACA_SECRET_KEY=your_secret_key
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_here

# Monitoring
LOG_LEVEL=INFO
ENABLE_METRICS=true
METRICS_PORT=9090
```

---

## 5. Phase 3: Database Migration

### 5.1 Schema Migration

**PostgreSQL Schema Creation**:
```sql
-- Create schemas
CREATE SCHEMA IF NOT EXISTS trading;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS system;

-- Set default search path
ALTER DATABASE trading_system SET search_path TO trading, analytics, system, public;

-- Create sequences
CREATE SEQUENCE trading.trading_cycle_seq START 1000;
CREATE SEQUENCE trading.trade_seq START 1;

-- Core tables with improved design
CREATE TABLE trading.trading_cycles (
    cycle_id VARCHAR(50) PRIMARY KEY,
    cycle_number BIGINT DEFAULT nextval('trading.trading_cycle_seq'),
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'running',
    securities_scanned INTEGER DEFAULT 0,
    patterns_analyzed INTEGER DEFAULT 0,
    signals_generated INTEGER DEFAULT 0,
    trades_executed INTEGER DEFAULT 0,
    total_pnl DECIMAL(15,2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE trading.services (
    service_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(100) NOT NULL UNIQUE,
    port INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'unknown',
    last_heartbeat TIMESTAMP WITH TIME ZONE,
    version VARCHAR(50),
    endpoint_url VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for performance
CREATE INDEX idx_trading_cycles_start_time ON trading.trading_cycles(start_time);
CREATE INDEX idx_trading_cycles_status ON trading.trading_cycles(status);
CREATE INDEX idx_services_status ON trading.services(status);
CREATE INDEX idx_services_last_heartbeat ON trading.services(last_heartbeat);
```

### 5.2 Data Migration Script

**SQLite to PostgreSQL Migration**:
```python
#!/usr/bin/env python3
"""
Database Migration Script: SQLite to PostgreSQL
Migrates all data from GitHub Codespaces SQLite to DigitalOcean PostgreSQL
"""

import sqlite3
import psycopg2
import os
from datetime import datetime
import logging

class DatabaseMigrator:
    def __init__(self, sqlite_path, postgres_url):
        self.sqlite_path = sqlite_path
        self.postgres_url = postgres_url
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('migration.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def migrate_all_data(self):
        """Execute complete data migration"""
        try:
            # Connect to both databases
            sqlite_conn = sqlite3.connect(self.sqlite_path)
            sqlite_conn.row_factory = sqlite3.Row
            
            postgres_conn = psycopg2.connect(self.postgres_url)
            postgres_cur = postgres_conn.cursor()
            
            # Migrate each table
            self.migrate_table('trading_cycles', sqlite_conn, postgres_cur)
            self.migrate_table('services', sqlite_conn, postgres_cur)
            self.migrate_table('selected_securities', sqlite_conn, postgres_cur)
            self.migrate_table('pattern_analysis', sqlite_conn, postgres_cur)
            self.migrate_table('trading_signals', sqlite_conn, postgres_cur)
            self.migrate_table('trade_records', sqlite_conn, postgres_cur)
            
            # Commit all changes
            postgres_conn.commit()
            self.logger.info("Migration completed successfully")
            
        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            postgres_conn.rollback()
            raise
        finally:
            sqlite_conn.close()
            postgres_conn.close()
    
    def migrate_table(self, table_name, sqlite_conn, postgres_cur):
        """Migrate a specific table"""
        self.logger.info(f"Migrating table: {table_name}")
        
        # Get all data from SQLite
        sqlite_cur = sqlite_conn.cursor()
        sqlite_cur.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cur.fetchall()
        
        if not rows:
            self.logger.info(f"No data to migrate for {table_name}")
            return
        
        # Get column names
        columns = [description[0] for description in sqlite_cur.description]
        
        # Create INSERT statement for PostgreSQL
        placeholders = ', '.join(['%s'] * len(columns))
        insert_sql = f"""
            INSERT INTO trading.{table_name} ({', '.join(columns)})
            VALUES ({placeholders})
            ON CONFLICT DO NOTHING
        """
        
        # Insert data in batches
        batch_size = 1000
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            data = [tuple(row) for row in batch]
            postgres_cur.executemany(insert_sql, data)
            self.logger.info(f"Migrated {len(data)} rows from {table_name}")

if __name__ == "__main__":
    sqlite_path = "./trading_system.db"
    postgres_url = os.getenv("DATABASE_URL")
    
    migrator = DatabaseMigrator(sqlite_path, postgres_url)
    migrator.migrate_all_data()
```

### 5.3 Database Connection Updates

**Updated Database Configuration**:
```python
# trading_config.py - PostgreSQL version

import os
import psycopg2
from psycopg2.pool import ThreadedConnectionPool

class DatabaseConfig:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.connection_pool = None
        self.init_connection_pool()
    
    def init_connection_pool(self):
        """Initialize PostgreSQL connection pool"""
        try:
            self.connection_pool = ThreadedConnectionPool(
                minconn=2,
                maxconn=20,
                dsn=self.database_url
            )
        except Exception as e:
            raise Exception(f"Failed to create connection pool: {e}")
    
    def get_connection(self):
        """Get connection from pool"""
        return self.connection_pool.getconn()
    
    def return_connection(self, conn):
        """Return connection to pool"""
        self.connection_pool.putconn(conn)
    
    def execute_query(self, query, params=None, fetch=False):
        """Execute query with automatic connection management"""
        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(query, params)
            
            if fetch:
                result = cur.fetchall()
            else:
                result = cur.rowcount
                
            conn.commit()
            return result
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                self.return_connection(conn)
```

---

## 6. Phase 4: Service Deployment

### 6.1 App Platform Deployment

**App Spec Configuration**:
```yaml
# .do/app.yaml
name: trading-application
region: sgp1  # Singapore region for Western Australia proximity
services:
- name: coordination-service
  source_dir: /
  dockerfile_path: Dockerfile.coordination
  github:
    repo: your-username/Trading_Application
    branch: main
    deploy_on_push: true
  instance_count: 2
  instance_size_slug: basic-xxs
  http_port: 5000
  health_check:
    http_path: /health
  env:
  - key: DATABASE_URL
    scope: RUN_TIME
    type: SECRET
  - key: REDIS_URL
    scope: RUN_TIME
    type: SECRET
  - key: IMPLEMENTATION_TYPE
    scope: RUN_TIME
    value: "rule-based"  # Current state
  - key: ML_READY
    scope: RUN_TIME
    value: "true"  # Infrastructure prepared
  routes:
  - path: /api/coordination
    preserve_path_prefix: true

- name: scanner-service
  source_dir: /
  dockerfile_path: Dockerfile.scanner
  github:
    repo: your-username/Trading_Application
    branch: main
    deploy_on_push: true
  instance_count: 2
  instance_size_slug: basic-xxs
  http_port: 5001
  health_check:
    http_path: /health
  env:
  - key: DATABASE_URL
    scope: RUN_TIME
    type: SECRET
  - key: COORDINATION_URL
    scope: RUN_TIME
    value: https://coordination-service
  routes:
  - path: /api/scanner
    preserve_path_prefix: true

# Additional services...

- name: web-dashboard
  source_dir: /
  dockerfile_path: Dockerfile.dashboard
  github:
    repo: your-username/Trading_Application
    branch: main
    deploy_on_push: true
  instance_count: 2
  instance_size_slug: basic-xxs
  http_port: 5010
  health_check:
    http_path: /health
  env:
  - key: DATABASE_URL
    scope: RUN_TIME
    type: SECRET
  routes:
  - path: /
    preserve_path_prefix: false

databases:
- name: trading-db
  engine: PG
  production: true
  cluster_name: trading-db-cluster

alerts:
- rule: CPU_UTILIZATION
  disabled: false
  operator: GREATER_THAN
  value: 80
  window: FIVE_MINUTES
```

### 6.2 Service Registration Updates

**Updated Service Registration**:
```python
# Updated coordination_service.py for App Platform

import os
import requests
from flask import Flask, request, jsonify

class CoordinationService:
    def __init__(self, db_url=None):
        self.app = Flask(__name__)
        self.db_url = db_url or os.getenv('DATABASE_URL')
        self.service_registry = {}
        self.setup_routes()
        
    def setup_routes(self):
        @self.app.route('/health')
        def health():
            return jsonify({
                'status': 'healthy',
                'service': 'coordination',
                'version': '1.0.0',
                'implementation': 'rule-based',  # Reflects current state
                'ml_ready': True,  # Infrastructure prepared
                'timestamp': datetime.utcnow().isoformat()
            })
        
        @self.app.route('/register_service', methods=['POST'])
        def register_service():
            data = request.json
            service_name = data.get('service_name')
            service_url = data.get('service_url')  # Full App Platform URL
            
            # Store in database and memory
            self.register_service_in_db(service_name, service_url)
            self.service_registry[service_name] = service_url
            
            return jsonify({'status': 'registered', 'service': service_name})
    
    def discover_services(self):
        """Auto-discover services in App Platform"""
        services = {
            'scanner': os.getenv('SCANNER_SERVICE_URL'),
            'patterns': os.getenv('PATTERNS_SERVICE_URL'),
            'technical': os.getenv('TECHNICAL_SERVICE_URL'),
            'execution': os.getenv('EXECUTION_SERVICE_URL'),
            'news': os.getenv('NEWS_SERVICE_URL'),
            'reports': os.getenv('REPORTS_SERVICE_URL'),
        }
        
        for name, url in services.items():
            if url:
                self.service_registry[name] = url
    
    def run(self):
        port = int(os.getenv('PORT', 5000))
        self.app.run(host='0.0.0.0', port=port)
```

### 6.3 Rule-Based System Migration

**Current Implementation Preservation**:
All current rule-based logic will be preserved during migration:

```python
# pattern_analysis.py - Current rule-based implementation
class PatternAnalysisService:
    def _detect_basic_patterns_fallback(self, symbol, data):
        """Manual pattern detection using price movement analysis"""
        patterns = []
        
        # Doji pattern detection (current implementation)
        for i in range(len(data)):
            candle = data.iloc[i]
            body_size = abs(candle['Close'] - candle['Open'])
            total_range = candle['High'] - candle['Low']
            
            if total_range > 0 and body_size / total_range < 0.1:
                patterns.append({
                    'type': 'doji',
                    'confidence': self._calculate_doji_confidence(candle),
                    'method': 'rule-based',  # Track implementation method
                    'index': i
                })
        
        return patterns
    
    def _prepare_for_ml_integration(self, patterns, data):
        """Prepare data structure for future ML integration"""
        # Log pattern data for future ML training
        for pattern in patterns:
            self._log_pattern_for_ml_training(pattern, data)
        
        return patterns
```

**Technical Analysis Signal Generation** (Rule-based):
```python
# technical_analysis.py - Current implementation
class TechnicalAnalysisService:
    def _generate_rule_based_signal(self, symbol, indicators, patterns):
        """Apply trading rules to generate signals"""
        signal_score = 0
        confidence_factors = []
        
        # Current weighted scoring system
        if patterns:
            pattern_score = sum(p['confidence'] for p in patterns) / len(patterns)
            signal_score += pattern_score * 0.35  # 35% weight
            confidence_factors.append(f"Pattern: {pattern_score:.2f}")
        
        # RSI analysis (current rules)
        if indicators.get('rsi'):
            rsi = indicators['rsi']
            if rsi < 30:  # Oversold
                signal_score += 25 * 0.30  # 30% weight
                confidence_factors.append("RSI: Oversold")
            elif rsi > 70:  # Overbought
                signal_score -= 25 * 0.30
                confidence_factors.append("RSI: Overbought")
        
        # Generate signal based on current logic
        if signal_score > 60:
            signal = 'BUY'
        elif signal_score < 40:
            signal = 'SELL'
        else:
            signal = 'HOLD'
            
        return {
            'signal': signal,
            'confidence': min(100, max(0, signal_score)),
            'method': 'rule-based',
            'factors': confidence_factors,
            'ml_ready': True  # Flag for future ML integration
        }
```

### 6.3 Load Balancer Configuration

**Load Balancer Setup**:
```bash
# Create load balancer in Singapore
doctl compute load-balancer create \
  --name trading-lb \
  --region sgp1 \
  --size lb-small \
  --algorithm round_robin \
  --vpc-uuid [VPC_UUID] \
  --health-check protocol:http,port:80,path:/health,check_interval_seconds:10 \
  --forwarding-rules entry_protocol:https,entry_port:443,target_protocol:http,target_port:80,certificate_id:[CERT_ID]
```

---

## 7. Phase 5: Security & Monitoring

### 7.1 Security Implementation

**Environment Secrets Management**:
```bash
# Store secrets in App Platform
doctl apps create-deployment [APP_ID] \
  --env DATABASE_URL="postgresql://user:pass@host:5432/db" \
  --env ALPACA_API_KEY="your_api_key" \
  --env ALPACA_SECRET_KEY="your_secret_key" \
  --env JWT_SECRET="your_jwt_secret" \
  --env REDIS_URL="redis://host:6379"
```

**SSL Certificate Setup**:
```bash
# Create Let's Encrypt certificate
doctl compute certificate create \
  --name trading-cert \
  --type lets_encrypt \
  --dns-names trading-app.yourdomain.com,api.trading-app.yourdomain.com
```

**Firewall Rules**:
```bash
# Create firewall
doctl compute firewall create \
  --name trading-firewall \
  --inbound-rules protocol:tcp,ports:22,source_addresses:0.0.0.0/0 \
  --inbound-rules protocol:tcp,ports:80,source_addresses:0.0.0.0/0 \
  --inbound-rules protocol:tcp,ports:443,source_addresses:0.0.0.0/0 \
  --outbound-rules protocol:tcp,ports:all,destination_addresses:0.0.0.0/0
```

### 7.2 Monitoring Setup

**Application Monitoring**:
```python
# monitoring.py
import os
import time
import psutil
import requests
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Metrics
REQUEST_COUNT = Counter('app_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('app_request_duration_seconds', 'Request latency')
ACTIVE_CONNECTIONS = Gauge('app_active_connections', 'Active connections')
CPU_USAGE = Gauge('app_cpu_usage_percent', 'CPU usage percentage')
MEMORY_USAGE = Gauge('app_memory_usage_bytes', 'Memory usage in bytes')

class ApplicationMonitoring:
    def __init__(self):
        self.start_time = time.time()
        
    def start_metrics_server(self):
        """Start Prometheus metrics server"""
        port = int(os.getenv('METRICS_PORT', 9090))
        start_http_server(port)
        
    def update_system_metrics(self):
        """Update system resource metrics"""
        CPU_USAGE.set(psutil.cpu_percent())
        MEMORY_USAGE.set(psutil.virtual_memory().used)
        
    def record_request(self, method, endpoint, duration):
        """Record request metrics"""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
        REQUEST_LATENCY.observe(duration)
```

**Health Check Enhancement**:
```python
# Enhanced health check
@app.route('/health')
def health_check():
    """Comprehensive health check"""
    health_status = {
        'status': 'healthy',
        'service': os.getenv('SERVICE_NAME'),
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'uptime': time.time() - start_time,
        'checks': {}
    }
    
    # Database connectivity check
    try:
        conn = get_db_connection()
        conn.execute('SELECT 1')
        health_status['checks']['database'] = 'healthy'
        conn.close()
    except Exception as e:
        health_status['checks']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # External service checks
    for service_name, service_url in service_registry.items():
        try:
            response = requests.get(f"{service_url}/health", timeout=5)
            if response.status_code == 200:
                health_status['checks'][service_name] = 'healthy'
            else:
                health_status['checks'][service_name] = f'unhealthy: HTTP {response.status_code}'
        except Exception as e:
            health_status['checks'][service_name] = f'unreachable: {str(e)}'
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code
```

### 7.3 Logging Configuration

**Centralized Logging**:
```python
# logging_config.py
import logging
import os
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Setup structured JSON logging"""
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Create handler
    handler = logging.StreamHandler()
    
    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger

# Usage in services
logger = setup_logging()

# Log with structured data
logger.info("Service started", extra={
    'service': 'coordination',
    'port': 5000,
    'environment': os.getenv('APP_ENV', 'production')
})
```

---

## 8. Phase 6: CI/CD Pipeline & ML Readiness

### 8.1 Current System Deployment Pipeline

The migration will maintain the current rule-based implementation while preparing infrastructure for future ML development per the ML Analysis Roadmap.

### 8.2 ML Infrastructure Preparation

**Future ML Components** (prepared but not implemented):
```yaml
# .do/app-ml-ready.yaml (future expansion)
name: trading-application-ml
region: sgp1

# ML Training Service (future implementation)
services:
- name: ml-training-service
  source_dir: /ml
  dockerfile_path: Dockerfile.ml-training
  instance_count: 0  # Disabled until Phase 2 ML development
  instance_size_slug: cpu-intel-4vcpu-8gb
  env:
  - key: ML_TRAINING_ENABLED
    value: "false"
  - key: MODEL_STORE_URL
    scope: RUN_TIME
    type: SECRET

# Pattern Training Data Collection
- name: pattern-data-collector
  source_dir: /
  dockerfile_path: Dockerfile.data-collector
  instance_count: 1
  instance_size_slug: basic-xxs
  env:
  - key: COLLECT_TRAINING_DATA
    value: "true"  # Start collecting data for future ML
  - key: DATABASE_URL
    scope: RUN_TIME
    type: SECRET
```

**Data Collection for Future ML Training**:
```python
# ml_data_collector.py (to be deployed)
class MLDataCollector:
    """
    Collects pattern detection and outcome data for future ML training
    as outlined in ML Analysis Roadmap
    """
    
    def log_pattern_detection(self, symbol, pattern_data, context):
        """Log all pattern detections for future ML training"""
        training_record = {
            'symbol': symbol,
            'timestamp': datetime.utcnow(),
            'pattern_type': pattern_data['type'],
            'confidence': pattern_data['confidence'],
            'method': 'rule-based',  # Current implementation
            
            # Context features for future ML
            'rsi': context.get('rsi'),
            'volume_surge': context.get('volume_surge'),
            'market_regime': context.get('market_regime'),
            'news_catalyst': context.get('news_catalyst', False),
            
            # Outcome tracking (updated later)
            'outcome_tracked': False,
            'max_gain': None,
            'max_loss': None,
            'pattern_success': None
        }
        
        self.save_training_record(training_record)
    
    def update_pattern_outcome(self, pattern_id, outcome_data):
        """Update pattern outcome for ML training data"""
        # This will support Ross Cameron's catalyst-based analysis
        # as outlined in the ML roadmap
        pass
```

### 8.3 GitHub Actions Workflow

**.github/workflows/deploy.yml**:
```yaml
name: Deploy to DigitalOcean

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: registry.digitalocean.com/trading-registry
  
jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:test_password@localhost:5432/test_db
      run: |
        python -m pytest tests/ --cov=./ --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Install doctl
      uses: digitalocean/action-doctl@v2
      with:
        token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}
    
    - name: Log in to DigitalOcean Container Registry
      run: doctl registry login --expiry-seconds 600
    
    - name: Build and push Docker images
      run: |
        # Build all service images
        docker build -f Dockerfile.coordination -t $REGISTRY/coordination:$GITHUB_SHA .
        docker build -f Dockerfile.scanner -t $REGISTRY/scanner:$GITHUB_SHA .
        docker build -f Dockerfile.patterns -t $REGISTRY/patterns:$GITHUB_SHA .
        docker build -f Dockerfile.technical -t $REGISTRY/technical:$GITHUB_SHA .
        docker build -f Dockerfile.execution -t $REGISTRY/execution:$GITHUB_SHA .
        docker build -f Dockerfile.news -t $REGISTRY/news:$GITHUB_SHA .
        docker build -f Dockerfile.reports -t $REGISTRY/reports:$GITHUB_SHA .
        docker build -f Dockerfile.dashboard -t $REGISTRY/dashboard:$GITHUB_SHA .
        
        # Push all images
        docker push $REGISTRY/coordination:$GITHUB_SHA
        docker push $REGISTRY/scanner:$GITHUB_SHA
        docker push $REGISTRY/patterns:$GITHUB_SHA
        docker push $REGISTRY/technical:$GITHUB_SHA
        docker push $REGISTRY/execution:$GITHUB_SHA
        docker push $REGISTRY/news:$GITHUB_SHA
        docker push $REGISTRY/reports:$GITHUB_SHA
        docker push $REGISTRY/dashboard:$GITHUB_SHA
    
    - name: Update App Platform deployment
      run: |
        # Update app spec with new image tags
        sed -i "s|image: $REGISTRY/coordination:.*|image: $REGISTRY/coordination:$GITHUB_SHA|g" .do/app.yaml
        sed -i "s|image: $REGISTRY/scanner:.*|image: $REGISTRY/scanner:$GITHUB_SHA|g" .do/app.yaml
        sed -i "s|image: $REGISTRY/patterns:.*|image: $REGISTRY/patterns:$GITHUB_SHA|g" .do/app.yaml
        sed -i "s|image: $REGISTRY/technical:.*|image: $REGISTRY/technical:$GITHUB_SHA|g" .do/app.yaml
        sed -i "s|image: $REGISTRY/execution:.*|image: $REGISTRY/execution:$GITHUB_SHA|g" .do/app.yaml
        sed -i "s|image: $REGISTRY/news:.*|image: $REGISTRY/news:$GITHUB_SHA|g" .do/app.yaml
        sed -i "s|image: $REGISTRY/reports:.*|image: $REGISTRY/reports:$GITHUB_SHA|g" .do/app.yaml
        sed -i "s|image: $REGISTRY/dashboard:.*|image: $REGISTRY/dashboard:$GITHUB_SHA|g" .do/app.yaml
        
        # Deploy to App Platform
        doctl apps update ${{ secrets.APP_ID }} --spec .do/app.yaml
    
    - name: Wait for deployment
      run: |
        doctl apps wait ${{ secrets.APP_ID }}
    
    - name: Run health checks
      run: |
        sleep 60  # Wait for services to start
        curl -f https://trading-app.yourdomain.com/health || exit 1
        curl -f https://api.trading-app.yourdomain.com/coordination/health || exit 1
```

### 8.2 Environment Management

**Development Environment**:
```yaml
# .do/app-dev.yaml
name: trading-application-dev
region: sgp1  # Singapore region
services:
  # Same services but with different configurations
  - name: coordination-service
    instance_count: 1
    instance_size_slug: basic-xxs
    env:
    - key: APP_ENV
      value: development
    - key: LOG_LEVEL
      value: DEBUG
    - key: IMPLEMENTATION_TYPE
      value: "rule-based"
    - key: ML_DATA_COLLECTION
      value: "enabled"  # Collect training data in dev
```

**Staging Environment**:
```yaml
# .do/app-staging.yaml
name: trading-application-staging
region: sgp1  # Singapore region
services:
  # Same services with staging configurations
  - name: coordination-service
    instance_count: 1
    instance_size_slug: basic-xs
    env:
    - key: APP_ENV
      value: staging
    - key: DATABASE_URL
      value: ${{ secrets.STAGING_DATABASE_URL }}
    - key: IMPLEMENTATION_TYPE
      value: "rule-based"
    - key: ML_READY
      value: "true"
```

---

## 9. Testing & Validation

### 9.1 Migration Testing Checklist

**Pre-Migration Tests**:
- [ ] All services run locally with Docker Compose
- [ ] Database migration script tested with sample data
- [ ] Environment variables properly configured
- [ ] Health checks return expected responses
- [ ] Inter-service communication works correctly

**Post-Migration Tests**:
- [ ] All services accessible via load balancer
- [ ] Database connectivity from all services
- [ ] Trading cycle execution end-to-end
- [ ] Real-time data feeds working
- [ ] API authentication and authorization
- [ ] Monitoring and alerting functional

### 9.2 Performance Testing

**Load Testing Script**:
```python
# load_test.py
import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor

async def test_endpoint(session, url, num_requests=100):
    """Test endpoint with concurrent requests"""
    start_time = time.time()
    
    async def make_request():
        async with session.get(url) as response:
            return response.status
    
    # Create tasks for concurrent requests
    tasks = [make_request() for _ in range(num_requests)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Calculate statistics
    successful = sum(1 for r in results if r == 200)
    failed = len(results) - successful
    rps = num_requests / duration
    
    return {
        'url': url,
        'total_requests': num_requests,
        'successful': successful,
        'failed': failed,
        'duration': duration,
        'requests_per_second': rps
    }

async def run_load_tests():
    """Run load tests on all endpoints"""
    endpoints = [
        'https://trading-app.yourdomain.com/health',
        'https://api.trading-app.yourdomain.com/coordination/health',
        'https://api.trading-app.yourdomain.com/scanner/health',
        'https://api.trading-app.yourdomain.com/patterns/health',
    ]
    
    async with aiohttp.ClientSession() as session:
        tasks = [test_endpoint(session, url) for url in endpoints]
        results = await asyncio.gather(*tasks)
        
        for result in results:
            print(f"URL: {result['url']}")
            print(f"RPS: {result['requests_per_second']:.2f}")
            print(f"Success Rate: {result['successful']}/{result['total_requests']}")
            print("-" * 50)

if __name__ == "__main__":
    asyncio.run(run_load_tests())
```

### 9.3 Integration Testing

**End-to-End Test**:
```python
# test_integration.py
import requests
import time
import pytest

class TestTradingSystemIntegration:
    
    @pytest.fixture
    def base_url(self):
        return "https://api.trading-app.yourdomain.com"
    
    def test_complete_trading_cycle(self, base_url):
        """Test complete trading cycle execution"""
        
        # 1. Start trading cycle
        response = requests.post(f"{base_url}/coordination/start_trading_cycle")
        assert response.status_code == 200
        cycle_data = response.json()
        cycle_id = cycle_data['cycle_id']
        
        # 2. Wait for cycle completion
        max_wait = 300  # 5 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            response = requests.get(f"{base_url}/coordination/trading_cycles")
            assert response.status_code == 200
            
            cycles = response.json()
            current_cycle = next((c for c in cycles if c['cycle_id'] == cycle_id), None)
            
            if current_cycle and current_cycle['status'] == 'completed':
                break
                
            time.sleep(10)
        else:
            pytest.fail("Trading cycle did not complete within timeout")
        
        # 3. Verify cycle results
        assert current_cycle['securities_scanned'] > 0
        assert current_cycle['patterns_analyzed'] >= 0
        assert 'total_pnl' in current_cycle
    
    def test_service_health_checks(self, base_url):
        """Test all service health endpoints"""
        services = [
            'coordination', 'scanner', 'patterns', 'technical',
            'execution', 'news', 'reports'
        ]
        
        for service in services:
            response = requests.get(f"{base_url}/{service}/health")
            assert response.status_code == 200
            
            health_data = response.json()
            assert health_data['status'] == 'healthy'
            assert 'service' in health_data
            assert 'timestamp' in health_data
```

---

## 10. Rollback Plan

### 10.1 Rollback Strategy

**Immediate Rollback Options**:
1. **App Platform Rollback**: Revert to previous deployment
2. **DNS Rollback**: Point domain back to GitHub Codespaces (if maintained)
3. **Database Rollback**: Restore from pre-migration backup

**Rollback Procedures**:
```bash
# 1. App Platform rollback to previous deployment
doctl apps list-deployments [APP_ID]
doctl apps create-deployment [APP_ID] --spec [PREVIOUS_SPEC_FILE]

# 2. Database rollback (if needed)
doctl databases backups list [DATABASE_ID]
doctl databases backups restore [DATABASE_ID] [BACKUP_ID]

# 3. DNS rollback (if GitHub Codespaces still running)
doctl domains records update [DOMAIN] [RECORD_ID] --data [OLD_IP]
```

### 10.2 Emergency Procedures

**Critical Issue Response**:
1. **Immediate Response** (< 5 minutes)
   - Scale down problematic services
   - Enable maintenance mode
   - Notify stakeholders

2. **Investigation** (< 15 minutes)
   - Check service logs
   - Verify database connectivity
   - Test individual service health

3. **Resolution** (< 30 minutes)
   - Apply hotfix if possible
   - Execute rollback if necessary
   - Restore service operation

**Emergency Contacts**:
- Technical Lead: [contact]
- Infrastructure Team: [contact]
- DigitalOcean Support: [support ticket]

---

## 11. Timeline & Resources

### 11.1 Migration Timeline

**Total Duration**: 4-6 weeks

**Phase Breakdown**:
- **Week 1**: Infrastructure setup and containerization
- **Week 2**: Database migration and service deployment
- **Week 3**: Security, monitoring, and CI/CD setup
- **Week 4**: Testing, validation, and final migration
- **Weeks 5-6**: Buffer time and optimization

**Detailed Schedule**:

| Phase | Duration | Dependencies | Deliverables |
|-------|----------|--------------|--------------|
| Infrastructure Setup | 3-5 days | DO account, domain | VPC, database, registry |
| Containerization | 5-7 days | Code review | Docker images, compose files |
| Database Migration | 3-5 days | Schema design | PostgreSQL setup, migration scripts |
| Service Deployment | 5-7 days | Container images | App Platform deployment |
| Security & Monitoring | 3-5 days | SSL certificates | Security policies, monitoring |
| CI/CD Pipeline | 3-5 days | GitHub setup | Automated deployment |
| Testing & Validation | 5-7 days | All previous phases | Test suite, performance validation |
| Production Migration | 1-2 days | All testing complete | Live production system |

### 11.2 Resource Requirements

**Technical Resources**:
- **DevOps Engineer**: Lead migration efforts
- **Backend Developer**: Application modifications
- **Database Administrator**: Schema design and migration
- **Security Engineer**: Security implementation

**DigitalOcean Resources**:
- **App Platform**: $20-50/month per service
- **Managed PostgreSQL**: $50-200/month (depending on size)
- **Load Balancer**: $10/month
- **Container Registry**: $5/month
- **Monitoring**: $10/month
- **Total Estimated Cost**: $300-500/month

### 11.3 Risk Assessment

**High-Risk Items**:
- Database migration complexity
- Service interdependency issues
- Performance degradation
- Security configuration errors

**Mitigation Strategies**:
- Comprehensive testing in staging environment
- Gradual migration with rollback checkpoints
- Performance monitoring throughout migration
- Security audit before production deployment

**Success Criteria**:
- [ ] All services operational with <1% downtime
- [ ] Database migration completed without data loss
- [ ] Performance meets or exceeds current benchmarks
- [ ] Security policies properly implemented
- [ ] CI/CD pipeline functional
- [ ] Monitoring and alerting operational
- [ ] Documentation updated and team trained
- [ ] Rule-based logic preserved and functional
- [ ] ML data collection infrastructure operational
- [ ] Infrastructure ready for Phase 2 ML development

---

## 12. Future ML Development Readiness

### 12.1 ML Infrastructure Prepared

**Data Collection Framework**:
The migration includes infrastructure to collect training data for future ML development as outlined in the ML Analysis Roadmap:

- Pattern detection logging with context
- Trading outcome tracking
- Technical indicator correlation data
- News catalyst event logging

**Planned ML Development Phases** (post-migration):

**Phase 1: ML-Enhanced Pattern Detection** (Months 2-3)
- Train models on collected pattern data
- Implement Ross Cameron's catalyst-based selection
- A/B test ML vs rule-based performance

**Phase 2: Technical Indicator Optimization** (Months 4-5)
- Discover optimal indicator thresholds
- Context-aware pattern recognition
- Dynamic scoring weight optimization

**Phase 3: Momentum Trading Integration** (Months 6+)
- "Stocks in Play" identification system
- News catalyst correlation analysis
- Advanced pattern prediction models

### 12.2 Infrastructure Scaling for ML

**Compute Resources** (prepared for activation):
```yaml
# ML training services (dormant until needed)
ml-training:
  instance_size_slug: cpu-intel-8vcpu-16gb
  autoscaling:
    min_instance_count: 0
    max_instance_count: 5

model-serving:
  instance_size_slug: basic-xs
  autoscaling:
    min_instance_count: 1
    max_instance_count: 10
```

**Storage Expansion**:
- Model artifacts storage in DO Spaces
- Training data warehouse (PostgreSQL)
- Feature store for real-time inference

---

## Conclusion

This migration plan provides a comprehensive roadmap for transitioning the Trading Application from GitHub Codespaces to a production-ready DigitalOcean infrastructure in Singapore, optimized for Western Australia users. The phased approach ensures minimal disruption while establishing a scalable, secure, and maintainable production environment.

**Key Migration Benefits**:
- **Production Scalability**: Handle increased load with auto-scaling
- **Regional Optimization**: Singapore deployment for optimal latency to Western Australia
- **High Availability**: Redundant services and managed database
- **Security**: Enterprise-grade security policies and SSL termination
- **Rule-Based Preservation**: All current trading logic maintained
- **ML Readiness**: Infrastructure prepared for future ML development per roadmap
- **Automation**: Full CI/CD pipeline for continuous deployment

**Current State Preserved**:
- All rule-based pattern detection algorithms maintained
- Manual technical analysis calculations preserved
- Fixed scoring and threshold systems operational
- No disruption to existing trading logic

**Future-Proofed for ML Development**:
- Data collection infrastructure for training ML models
- Scalable compute resources for model training
- A/B testing framework for ML vs rule-based comparison
- Support for Ross Cameron's catalyst-based trading methodology

The plan balances thorough preparation with practical implementation, providing clear steps, timelines, and fallback procedures to ensure a successful migration while preparing for the planned ML evolution outlined in the ML Analysis Roadmap.