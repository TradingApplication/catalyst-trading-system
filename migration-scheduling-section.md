# Addition to Cloud Migration Plan

## Environment Preparation - Scheduling Infrastructure

### News Collection Scheduling (Post-Migration)

Once migrated to DigitalOcean, implement the following scheduling infrastructure:

#### 1. Cron-based Scheduling for News Collection

**Pre-Market Aggressive Collection (4:00 AM - 9:30 AM EST)**
```bash
# Every 5 minutes during pre-market
*/5 4-9 * * 1-5 /usr/bin/python3 /app/news_collection_scheduler.py --mode=aggressive
```

**Regular Hours Collection (9:30 AM - 4:00 PM EST)**
```bash
# Every 30 minutes during market hours
*/30 9-16 * * 1-5 /usr/bin/python3 /app/news_collection_scheduler.py --mode=normal
```

**After-Hours Collection (4:00 PM - 8:00 PM EST)**
```bash
# Every hour after market close
0 16-20 * * 1-5 /usr/bin/python3 /app/news_collection_scheduler.py --mode=light
```

**Weekend Collection**
```bash
# Every 2 hours on weekends
0 */2 * * 0,6 /usr/bin/python3 /app/news_collection_scheduler.py --mode=weekend
```

#### 2. DigitalOcean App Platform Scheduled Jobs

Alternative to cron, using DO App Platform's scheduled jobs feature:

```yaml
# .do/app.yaml addition
jobs:
- name: news-collector-premarket
  kind: PRE_DEPLOY
  source_dir: /
  dockerfile_path: Dockerfile.scheduler
  instance_count: 1
  instance_size_slug: basic-xxs
  run_command: python news_collection_scheduler.py --mode=aggressive
  schedule:
    # Run every 5 minutes from 4 AM to 9:30 AM EST
    cron: "*/5 4-9 * * 1-5"
  env:
  - key: DATABASE_URL
    scope: RUN_TIME
    type: SECRET
  - key: COLLECTION_MODE
    value: "aggressive"

- name: news-collector-regular
  kind: PRE_DEPLOY
  source_dir: /
  dockerfile_path: Dockerfile.scheduler
  instance_count: 1
  instance_size_slug: basic-xxs
  run_command: python news_collection_scheduler.py --mode=normal
  schedule:
    cron: "*/30 9-16 * * 1-5"
  env:
  - key: DATABASE_URL
    scope: RUN_TIME
    type: SECRET
```

#### 3. Scheduler Service Script

Create `news_collection_scheduler.py`:

```python
#!/usr/bin/env python3
"""
News Collection Scheduler
Handles scheduled news collection based on market hours
"""

import sys
import argparse
import requests
import logging
from datetime import datetime

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('news_scheduler')

def trigger_collection(mode, logger):
    """Trigger news collection via API"""
    try:
        # Call news service API
        response = requests.post(
            'http://news-service:5008/collect_news',
            json={
                'sources': 'all',
                'mode': mode
            },
            timeout=300  # 5 minute timeout for collection
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Collection successful: {result['articles_collected']} articles")
            return True
        else:
            logger.error(f"Collection failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error triggering collection: {e}")
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['aggressive', 'normal', 'light', 'weekend'], 
                       default='normal')
    args = parser.parse_args()
    
    logger = setup_logging()
    logger.info(f"Starting scheduled collection in {args.mode} mode")
    
    success = trigger_collection(args.mode, logger)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

#### 4. Monitoring & Alerting

**Collection Health Checks**
```yaml
alerts:
- rule: SCHEDULED_JOB_FAILURE
  disabled: false
  operator: GREATER_THAN
  value: 2  # Alert after 2 consecutive failures
  window: FIFTEEN_MINUTES
  entities:
  - "news-collector-premarket"
  - "news-collector-regular"
```

**Performance Metrics to Track**
- Articles collected per run
- Collection duration
- API rate limit usage
- Database growth rate
- Duplicate rate

#### 5. Database Maintenance

**Scheduled cleanup jobs:**
```sql
-- Archive old news (run weekly)
INSERT INTO news_archive 
SELECT * FROM news_raw 
WHERE collected_timestamp < datetime('now', '-30 days');

DELETE FROM news_raw 
WHERE collected_timestamp < datetime('now', '-30 days');

-- Vacuum database (run daily)
VACUUM;
ANALYZE;
```

### Important Notes

1. **Time Zones**: All schedules in EST/EDT to match market hours
2. **Rate Limits**: Monitor API usage to avoid hitting free tier limits
3. **Scaling**: Pre-market collection may need multiple workers
4. **Failover**: If scheduled job fails, next run catches up
5. **Storage**: Plan for ~1GB/month of news data growth

### Pre-Migration Testing

Before migration, test scheduling logic locally:
```bash
# Simulate scheduled runs
python news_collection_scheduler.py --mode=aggressive
python news_collection_scheduler.py --mode=normal
```

This ensures smooth transition from manual Codespaces operation to automated cloud scheduling.