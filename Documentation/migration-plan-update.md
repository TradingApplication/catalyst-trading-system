# Migration Plan Updates for v2.0.0 Architecture

**Date**: June 27, 2025  
**Purpose**: Update cloud migration plan for news-driven architecture

## Key Architecture Changes

### Service Updates Required

1. **News Collection Service (v2.0.0)** - NEW
   - Multi-source news aggregation
   - Source alignment tracking
   - Outcome tracking for ML
   - Pre-market aggressive collection

2. **Security Scanner Service (v2.0.0)** - REWRITTEN
   - News-driven selection (not random)
   - Catalyst scoring algorithm
   - Outputs to trading_candidates table

3. **Coordination Service (v2.0.0)** - UPDATED
   - New workflow orchestration
   - Pre-market aggressive mode
   - Outcome tracking integration

### Database Schema Updates

**New Tables Required**:
```sql
-- Enhanced news tracking
news_raw (with source alignment fields)
trading_candidates
trading_scans
source_metrics
narrative_clusters

-- Coordination tables
trading_cycles
service_health
workflow_log
```

### Environment Variables Update

Add to `.do/app.yaml`:
```yaml
env:
- key: NEWSAPI_KEY
  scope: RUN_TIME
  type: SECRET
- key: ALPHAVANTAGE_KEY
  scope: RUN_TIME
  type: SECRET
- key: FINNHUB_KEY
  scope: RUN_TIME
  type: SECRET
- key: NEWS_COLLECTION_MODE
  value: "aggressive"
- key: SOURCE_TRACKING_ENABLED
  value: "true"
```

### Scheduled Jobs Update

Replace existing schedulers with:

```yaml
jobs:
- name: news-collector-premarket
  source_dir: /
  dockerfile_path: Dockerfile.scheduler
  run_command: python coordination_service.py --trigger-cycle --mode=aggressive
  schedule:
    cron: "*/5 4-9 * * 1-5"  # Every 5 min pre-market
  env:
  - key: CYCLE_MODE
    value: "aggressive"

- name: news-source-analyzer
  source_dir: /
  dockerfile_path: Dockerfile.analyzer
  run_command: python analyze_sources.py
  schedule:
    cron: "0 22 * * *"  # Daily at 10 PM
```

### Service Start Order (Updated)

1. PostgreSQL Database
2. Redis Cache
3. **News Collection Service** (must be first)
4. Coordination Service
5. Security Scanner (depends on news)
6. Pattern Analysis
7. Technical Analysis
8. Paper Trading
9. Web Dashboard

### Container Updates

**News Collection Service Dockerfile**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy news service
COPY news_collection_service_v200.py .
COPY database_utils.py .

ENV PORT=5008
ENV SERVICE_NAME=news_collection

HEALTHCHECK --interval=30s --timeout=10s \
  CMD curl -f http://localhost:5008/health || exit 1

EXPOSE 5008

CMD ["python", "news_collection_service_v200.py"]
```

### Data Migration Additions

Update migration script to include:
```python
# Additional tables to migrate
tables_to_migrate = [
    'news_raw',           # New schema with alignment fields
    'trading_candidates', # New table
    'source_metrics',     # New table
    'narrative_clusters', # New table
    'trading_cycles',     # Updated schema
    # ... existing tables
]
```

### Monitoring Updates

Add new metrics:
```yaml
alerts:
- rule: NEWS_COLLECTION_FAILURE
  operator: LESS_THAN
  value: 100  # Expect 100+ articles per hour
  window: ONE_HOUR
  entities: ["news-collection-service"]

- rule: SOURCE_ACCURACY_DEGRADATION
  operator: LESS_THAN
  value: 80  # Source accuracy below 80%
  window: ONE_DAY
  entities: ["source-analysis-job"]
```

### Storage Considerations

**Increased Storage Needs**:
- news_raw: ~5GB/month (with all metadata)
- trading_candidates: ~500MB/month
- source_metrics: ~100MB/month

Plan for 10GB/month growth initially.

### Pre-Migration Testing

Before migration, test:
1. News collection from all sources
2. Source tier classification
3. Scanner using news data
4. Coordination workflow end-to-end
5. Outcome tracking updates

### Migration Sequence

1. **Phase 1**: Database and infrastructure
2. **Phase 2**: Deploy news collection service first
3. **Phase 3**: Let news collection run for 24 hours to build data
4. **Phase 4**: Deploy remaining services
5. **Phase 5**: Enable scheduling
6. **Phase 6**: Monitor and optimize

### Rollback Considerations

If issues arise:
1. Scanner can fall back to symbol list
2. News service can run standalone
3. Keep old services available for 48 hours

### Performance Targets

- News collection: < 5 min for all sources
- Scanner: < 30 seconds to identify top 5
- Full workflow: < 5 minutes end-to-end
- Pre-market aggressive: < 2 minutes

### Cost Implications

Additional monthly costs:
- Increased storage: +$5-10
- News API subscriptions: $0-50 (using free tiers)
- Additional compute for analysis: +$10-20
- Total increase: ~$20-80/month

### Success Criteria

- [ ] 1000+ news articles collected daily
- [ ] 50+ securities scanned from news daily
- [ ] 5 high-quality picks per market session
- [ ] Source accuracy tracking operational
- [ ] Narrative clustering detecting patterns
- [ ] Outcome tracking feeding back to news

This positions us for true news-driven trading with ML readiness!