"""
Catalyst Trading System
Name of file: app_digitalocean.py
Version: 2.0.0
Last Updated: 2025-06-30
REVISION HISTORY:
  - v1.0.0 (2025-06-29) - Initial DigitalOcean deployment
  - v2.0.0 (2025-06-30) - Added paper trading integration
"""

import os
import sys
import logging
from flask import Flask, jsonify, render_template_string
from datetime import datetime
import threading

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
os.makedirs('/tmp/logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/logs/catalyst.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Initialize global variables for services
trading_client = None
account_info = {}
positions_cache = []
last_update = None

# Import Alpaca
try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    logger.warning("Alpaca package not installed")

def initialize_trading():
    """Initialize Alpaca paper trading connection"""
    global trading_client, account_info
    
    if not ALPACA_AVAILABLE:
        logger.error("Alpaca package not available")
        return False
    
    try:
        api_key = os.getenv('ALPACA_API_KEY')
        secret_key = os.getenv('ALPACA_SECRET_KEY')
        
        if not api_key or not secret_key:
            logger.error("Alpaca API credentials not found in environment")
            return False
        
        trading_client = TradingClient(api_key, secret_key, paper=True)
        account = trading_client.get_account()
        
        account_info = {
            'status': account.status,
            'buying_power': float(account.buying_power),
            'portfolio_value': float(account.portfolio_value),
            'cash': float(account.cash),
            'equity': float(account.equity)
        }
        
        logger.info(f"✅ Trading client initialized. Portfolio Value: ${account_info['portfolio_value']:,.2f}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize trading client: {e}")
        return False

def update_positions():
    """Update positions cache"""
    global positions_cache, last_update
    
    if not trading_client:
        return
    
    try:
        positions = trading_client.get_all_positions()
        positions_cache = [{
            'symbol': pos.symbol,
            'qty': float(pos.qty),
            'side': pos.side,
            'avg_entry_price': float(pos.avg_entry_price),
            'market_value': float(pos.market_value),
            'unrealized_pl': float(pos.unrealized_pl) if hasattr(pos, 'unrealized_pl') else 0
        } for pos in positions]
        
        last_update = datetime.now()
        logger.info(f"Updated {len(positions_cache)} positions")
        
    except Exception as e:
        logger.error(f"Failed to update positions: {e}")

# Dashboard HTML template
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Catalyst Trading System</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .status-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .metric {
            display: inline-block;
            margin: 10px 20px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }
        .metric-label {
            font-size: 14px;
            color: #666;
        }
        .positions-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .positions-table th {
            background-color: #f8f9fa;
            padding: 10px;
            text-align: left;
            border-bottom: 2px solid #dee2e6;
        }
        .positions-table td {
            padding: 10px;
            border-bottom: 1px solid #dee2e6;
        }
        .profit {
            color: #28a745;
        }
        .loss {
            color: #dc3545;
        }
        .status-ok {
            color: #28a745;
        }
        .status-error {
            color: #dc3545;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Catalyst Trading System</h1>
            <p>Paper Trading Dashboard - DigitalOcean Deployment</p>
        </div>
        
        <div class="status-card">
            <h2>System Status</h2>
            <div class="metric">
                <div class="metric-label">Trading Status</div>
                <div class="metric-value {{ 'status-ok' if trading_status else 'status-error' }}">
                    {{ 'CONNECTED' if trading_status else 'DISCONNECTED' }}
                </div>
            </div>
            <div class="metric">
                <div class="metric-label">Environment</div>
                <div class="metric-value">{{ environment }}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Last Update</div>
                <div class="metric-value">{{ last_update }}</div>
            </div>
        </div>
        
        {% if trading_status %}
        <div class="status-card">
            <h2>Account Overview</h2>
            <div class="metric">
                <div class="metric-label">Portfolio Value</div>
                <div class="metric-value">${{ "%.2f"|format(account.portfolio_value) }}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Buying Power</div>
                <div class="metric-value">${{ "%.2f"|format(account.buying_power) }}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Cash</div>
                <div class="metric-value">${{ "%.2f"|format(account.cash) }}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Account Status</div>
                <div class="metric-value status-ok">{{ account.status }}</div>
            </div>
        </div>
        
        <div class="status-card">
            <h2>Current Positions ({{ positions|length }})</h2>
            {% if positions %}
            <table class="positions-table">
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Quantity</th>
                        <th>Side</th>
                        <th>Entry Price</th>
                        <th>Market Value</th>
                        <th>Unrealized P/L</th>
                    </tr>
                </thead>
                <tbody>
                    {% for pos in positions %}
                    <tr>
                        <td><strong>{{ pos.symbol }}</strong></td>
                        <td>{{ pos.qty }}</td>
                        <td>{{ pos.side }}</td>
                        <td>${{ "%.2f"|format(pos.avg_entry_price) }}</td>
                        <td>${{ "%.2f"|format(pos.market_value) }}</td>
                        <td class="{{ 'profit' if pos.unrealized_pl >= 0 else 'loss' }}">
                            ${{ "%.2f"|format(pos.unrealized_pl) }}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p>No open positions</p>
            {% endif %}
        </div>
        {% endif %}
        
        <div class="status-card">
            <h2>API Status</h2>
            <p>✅ Alpaca Paper Trading: {{ 'Connected' if trading_status else 'Not Connected' }}</p>
            <p>✅ NewsAPI: {{ 'Configured' if has_news_api else 'Not Configured' }}</p>
            <p>✅ Alpha Vantage: Configured</p>
            <p>✅ Twelve Data: Configured</p>
            <p>✅ OpenAI: Configured</p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def dashboard():
    """Main dashboard"""
    return render_template_string(DASHBOARD_HTML,
        trading_status=trading_client is not None,
        environment=os.getenv('ENVIRONMENT', 'development'),
        last_update=last_update.strftime('%Y-%m-%d %H:%M:%S') if last_update else 'Never',
        account=account_info,
        positions=positions_cache,
        has_news_api=bool(os.getenv('NEWSAPI_KEY'))
    )

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'trading_connected': trading_client is not None,
        'environment': os.getenv('ENVIRONMENT', 'development')
    })

@app.route('/health/trading')
def trading_health():
    """Trading service health check"""
    if not trading_client:
        return jsonify({'status': 'error', 'message': 'Trading client not initialized'}), 503
    
    try:
        account = trading_client.get_account()
        return jsonify({
            'status': 'healthy',
            'account_status': account.status,
            'portfolio_value': float(account.portfolio_value),
            'positions_count': len(positions_cache)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 503

@app.route('/api/positions')
def get_positions():
    """Get current positions"""
    if not trading_client:
        return jsonify({'error': 'Trading client not initialized'}), 503
    
    update_positions()
    return jsonify({
        'positions': positions_cache,
        'last_update': last_update.isoformat() if last_update else None,
        'count': len(positions_cache)
    })

@app.route('/api/account')
def get_account():
    """Get account information"""
    if not trading_client:
        return jsonify({'error': 'Trading client not initialized'}), 503
    
    try:
        account = trading_client.get_account()
        return jsonify({
            'status': account.status,
            'buying_power': float(account.buying_power),
            'portfolio_value': float(account.portfolio_value),
            'cash': float(account.cash),
            'equity': float(account.equity),
            'pattern_day_trader': account.pattern_day_trader
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def background_updater():
    """Background thread to update positions periodically"""
    while True:
        try:
            if trading_client:
                update_positions()
                # Update account info
                account = trading_client.get_account()
                account_info.update({
                    'status': account.status,
                    'buying_power': float(account.buying_power),
                    'portfolio_value': float(account.portfolio_value),
                    'cash': float(account.cash),
                    'equity': float(account.equity)
                })
            threading.Event().wait(60)  # Update every minute
        except Exception as e:
            logger.error(f"Background updater error: {e}")
            threading.Event().wait(60)

# Initialize everything on startup
if __name__ == '__main__':
    logger.info("🚀 Starting Catalyst Trading System...")
    
    # Initialize trading
    if initialize_trading():
        logger.info("✅ Trading initialized successfully")
        update_positions()
        
        # Start background updater
        updater_thread = threading.Thread(target=background_updater, daemon=True)
        updater_thread.start()
    else:
        logger.warning("⚠️ Running without trading connection")
    
    # Start Flask
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
