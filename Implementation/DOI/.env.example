# =============================================================================
# CATALYST TRADING SYSTEM - ENVIRONMENT CONFIGURATION
# DigitalOcean Deployment Configuration
# =============================================================================

# -----------------------------------------------------------------------------
# DATABASE CONFIGURATION (DigitalOcean Managed PostgreSQL)
# -----------------------------------------------------------------------------
# Format: postgresql://username:password@host:port/database?sslmode=require
# Get this URL from your DigitalOcean database dashboard
DATABASE_URL=postgresql://catalyst_app:YOUR_DB_PASSWORD@db-catalyst-trading-do-user-XXXXX-0.b.db.ondigitalocean.com:25060/catalyst_trading?sslmode=require

# -----------------------------------------------------------------------------
# NEWS DATA SOURCES
# -----------------------------------------------------------------------------
# NewsAPI.org - Free tier: 1000 requests/month
NEWSAPI_KEY=your_newsapi_key_here

# Alpha Vantage - Free tier: 5 API requests per minute
ALPHAVANTAGE_KEY=your_alphavantage_key_here

# Finnhub - Free tier: 60 API calls/minute
FINNHUB_KEY=your_finnhub_key_here

# -----------------------------------------------------------------------------
# TRADING CONFIGURATION (Alpaca Paper Trading)
# -----------------------------------------------------------------------------
# Alpaca Paper Trading Account (FREE)
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# -----------------------------------------------------------------------------
# RISK MANAGEMENT PARAMETERS
# -----------------------------------------------------------------------------
# Maximum number of concurrent positions
MAX_POSITIONS=5

# Maximum position size as percentage of total capital (20% = $1000 of $5000)
POSITION_SIZE_PCT=20

# Pre-market position size limit (more conservative)
PREMARKET_POSITION_PCT=10

# Default stop loss percentage
STOP_LOSS_PCT=2

# Minimum catalyst score to consider trading (0-100)
MIN_CATALYST_SCORE=30

# Maximum daily trades
MAX_DAILY_TRADES=20

# -----------------------------------------------------------------------------
# TRADING SCHEDULE CONFIGURATION
# -----------------------------------------------------------------------------
# Pre-market aggressive mode (EST times)
PREMARKET_START=04:00
PREMARKET_END=09:30
PREMARKET_INTERVAL_MINUTES=5

# Regular market hours
MARKET_START=09:30
MARKET_END=16:00
MARKET_INTERVAL_MINUTES=30

# After-hours light mode
AFTERHOURS_START=16:00
AFTERHOURS_END=20:00
AFTERHOURS_INTERVAL_MINUTES=60

# -----------------------------------------------------------------------------
# PATTERN ANALYSIS CONFIGURATION
# -----------------------------------------------------------------------------
# Minimum price for consideration (avoid penny stocks)
MIN_PRICE=1.00

# Maximum price to avoid super high-priced stocks
MAX_PRICE=500.00

# Minimum volume for liquidity
MIN_VOLUME=500000

# Minimum relative volume (1.5 = 50% above average)
MIN_RELATIVE_VOLUME=1.5

# Minimum price change percentage to consider
MIN_PRICE_CHANGE=2.0

# -----------------------------------------------------------------------------
# NEWS FILTERING CONFIGURATION
# -----------------------------------------------------------------------------
# Source tier weights (1.0 = highest reliability)
TIER_1_WEIGHT=1.0
TIER_2_WEIGHT=0.8
TIER_3_WEIGHT=0.6
TIER_4_WEIGHT=0.4
TIER_5_WEIGHT=0.2

# Keyword multipliers
EARNINGS_MULTIPLIER=1.2
FDA_MULTIPLIER=1.5
MERGER_MULTIPLIER=1.3
DEFAULT_MULTIPLIER=1.0

# Market state multipliers
PREMARKET_MULTIPLIER=2.0
REGULAR_MULTIPLIER=1.0
AFTERHOURS_MULTIPLIER=0.8

# -----------------------------------------------------------------------------
# SECURITY CONFIGURATION
# -----------------------------------------------------------------------------
# JWT secret for dashboard authentication (generate a random string)
JWT_SECRET=your_very_secure_random_jwt_secret_here_at_least_32_characters

# Flask secret key (generate a random string)
FLASK_SECRET_KEY=your_very_secure_random_flask_secret_here

# Admin dashboard password
ADMIN_PASSWORD=your_secure_admin_password_here

# -----------------------------------------------------------------------------
# SYSTEM CONFIGURATION
# -----------------------------------------------------------------------------
# Logging level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO

# Timezone for trading operations
TIMEZONE=US/Eastern

# Enable metrics collection
ENABLE_METRICS=true

# Metrics port for Prometheus
METRICS_PORT=9090

# -----------------------------------------------------------------------------
# EXTERNAL SERVICE TIMEOUTS
# -----------------------------------------------------------------------------
# API request timeouts in seconds
NEWS_API_TIMEOUT=30
TRADING_API_TIMEOUT=10
DATABASE_TIMEOUT=30

# Service health check timeout
HEALTH_CHECK_TIMEOUT=5

# -----------------------------------------------------------------------------
# CACHE CONFIGURATION
# -----------------------------------------------------------------------------
# Redis cache TTL in seconds
NEWS_CACHE_TTL=3600
CANDIDATE_CACHE_TTL=1800
SIGNAL_CACHE_TTL=300

# -----------------------------------------------------------------------------
# BACKUP CONFIGURATION
# -----------------------------------------------------------------------------
# DigitalOcean Spaces for backups (optional)
# SPACES_ACCESS_KEY=your_spaces_access_key
# SPACES_SECRET_KEY=your_spaces_secret_key
# SPACES_BUCKET=catalyst-trading-backups
# SPACES_REGION=sgp1

# -----------------------------------------------------------------------------
# NOTIFICATION CONFIGURATION (optional)
# -----------------------------------------------------------------------------
# Email alerts for significant events
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=your_email@gmail.com
# SMTP_PASSWORD=your_app_password
# ALERT_EMAIL=your_alerts@gmail.com

# Slack webhook for trading alerts (optional)
# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# -----------------------------------------------------------------------------
# DEVELOPMENT vs PRODUCTION
# -----------------------------------------------------------------------------
# Environment: development, staging, production
ENVIRONMENT=production

# Enable debug mode (never set to true in production)
DEBUG=false

# Enable development features
DEV_MODE=false

# =============================================================================
# SETUP INSTRUCTIONS:
# =============================================================================
# 1. Copy this file to .env in your project root
# 2. Replace all placeholder values with your actual credentials
# 3. Get DigitalOcean database URL from your managed database dashboard
# 4. Sign up for free API keys:
#    - NewsAPI: https://newsapi.org/
#    - Alpha Vantage: https://www.alphavantage.co/
#    - Finnhub: https://finnhub.io/
#    - Alpaca: https://alpaca.markets/ (paper trading account)
# 5. Generate secure random strings for JWT_SECRET and FLASK_SECRET_KEY
# 6. Set a secure admin password
# 7. Adjust risk parameters according to your trading capital
# =============================================================================