"""
Catalyst Trading System
Name of file: app.py
Version: 5.0.0
Last Updated: 2025-06-30
REVISION HISTORY:
  - v1.0.0 (2025-06-29) - Initial DigitalOcean deployment
  - v2.0.0 (2025-06-30) - Added paper trading integration
  - v3.0.0 (2025-06-30) - Added community profit scanner
  - v4.0.0 (2025-06-30) - Added news service
  - v5.0.0 (2025-06-30) - Fully integrated catalyst system
"""

import os
import sys
import logging
from flask import Flask, jsonify, render_template_string, request
from datetime import datetime
import threading

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our services
from scanner_service import init_scanner
from news_service import init_news_service

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

# Initialize global variables
trading_client = None
account_info = {}
positions_cache = []
last_update = None
scanner_opportunities = []
news_headlines = []

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

def update_scanner_results():
    """Update scanner results from scanner service"""
    global scanner_opportunities
    
    try:
        if app.extensions.get('scanner_service'):
            scanner_opportunities = app.extensions['scanner_service'].scan_cache.get('final_picks', [])
            logger.info(f"Updated scanner with {len(scanner_opportunities)} opportunities")
    except Exception as e:
        logger.error(f"Failed to update scanner results: {e}")

def update_news_headlines():
    """Get latest news headlines for display"""
    global news_headlines
    
    try:
        if app.extensions.get('news_service'):
            # Get news for top opportunities
            headlines = []
            for opp in scanner_opportunities[:3]:
                symbol = opp.get('symbol')
                if symbol:
                    news_items = app.extensions['news_service'].collect_news(symbol)
                    for item in news_items[:2]:  # Top 2 per symbol
                        headlines.append({
                            'symbol': symbol,
                            'headline': item['headline'],
                            'impact': item['impact_score'],
                            'keywords': item['keywords']
                        })
            news_headlines = headlines[:5]  # Total 5 headlines
    except Exception as e:
        logger.error(f"Failed to update news: {e}")

# Enhanced Dashboard HTML
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Catalyst Trading System - Community Impact</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .mission {
            background: #e8f5e9;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #4caf50;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .status-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
        .opportunities-table, .positions-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .opportunities-table th, .positions-table th {
            background-color: #f8f9fa;
            padding: 10px;
            text-align: left;
            border-bottom: 2px solid #dee2e6;
        }
        .opportunities-table td, .positions-table td {
            padding: 10px;
            border-bottom: 1px solid #dee2e6;
        }
        .buy {
            color: #28a745;
            font-weight: bold;
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
        .confidence-high {
            background: #d4edda;
            padding: 3px 8px;
            border-radius: 4px;
        }
        .confidence-medium {
            background: #fff3cd;
            padding: 3px 8px;
            border-radius: 4px;
        }
        .news-item {
            background: #f8f9fa;
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 3px solid #007bff;
        }
        .news-symbol {
            font-weight: bold;
            color: #007bff;
        }
        .news-keywords {
            font-size: 0.8em;
            color: #6c757d;
        }
        .catalyst-badge {
            background: #ff6b6b;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.8em;
            margin-left: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Catalyst Trading System - Community Impact</h1>
            <p>AI-Powered Trading for Social Good</p>
        </div>
        
        <div class="mission">
            <strong>Our Mission:</strong> Use advanced catalyst detection and technical analysis to generate consistent profits for community initiatives. Every trade brings us closer to funding education, healthcare, and opportunity programs.
        </div>
        
        <div class="grid">
            <div class="status-card">
                <h2>System Status</h2>
                <div class="metric">
                    <div class="metric-label">Trading Status</div>
                    <div class="metric-value {{ 'status-ok' if trading_status else 'status-error' }}">
                        {{ 'CONNECTED' if trading_status else 'DISCONNECTED' }}
                    </div>
                </div>
                <div class="metric">
                    <div class="metric-label">Scanner Status</div>
                    <div class="metric-value {{ 'status-ok' if scanner_active else 'status-error' }}">
                        {{ 'ACTIVE' if scanner_active else 'INACTIVE' }}
                    </div>
                </div>
                <div class="metric">
                    <div class="metric-label">News Service</div>
                    <div class="metric-value {{ 'status-ok' if news_active else 'status-error' }}">
                        {{ 'ACTIVE' if news_active else 'INACTIVE' }}
                    </div>
                </div>
            </div>
            
            {% if trading_status %}
            <div class="status-card">
                <h2>Portfolio Performance</h2>
                <div class="metric">
                    <div class="metric-label">Total Value</div>
                    <div class="metric-value">${{ "%.2f"|format(account.portfolio_value) }}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Available Cash</div>
                    <div class="metric-value">${{ "%.2f"|format(account.cash) }}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Positions</div>
                    <div class="metric-value">{{ positions|length }}</div>
                </div>
            </div>
            {% endif %}
        </div>
        
        {% if news_headlines %}
        <div class="status-card">
            <h2>📰 Latest Market Catalysts</h2>
            {% for news in news_headlines %}
            <div class="news-item">
                <span class="news-symbol">{{ news.symbol }}</span>
                {{ news.headline[:100] }}...
                {% if news.keywords %}
                <div class="news-keywords">
                    Keywords: {{ news.keywords|join(', ') }}
                    <span class="catalyst-badge">Impact: {{ "%.1f"|format(news.impact * 10) }}/10</span>
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        <div class="status-card">
            <h2>🎯 Trading Opportunities (Top {{ opportunities|length }})</h2>
            {% if opportunities %}
            <table class="opportunities-table">
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Action</th>
                        <th>Entry</th>
                        <th>Stop Loss</th>
                        <th>Target</th>
                        <th>Confidence</th>
                        <th>Catalyst/Reason</th>
                    </tr>
                </thead>
                <tbody>
                    {% for opp in opportunities %}
                    <tr>
                        <td><strong>{{ opp.symbol }}</strong></td>
                        <td class="buy">{{ opp.action }}</td>
                        <td>${{ "%.2f"|format(opp.entry_price) }}</td>
                        <td>${{ "%.2f"|format(opp.stop_loss) }}</td>
                        <td>${{ "%.2f"|format(opp.take_profit) }}</td>
                        <td>
                            <span class="{{ 'confidence-high' if opp.confidence > 0.7 else 'confidence-medium' }}">
                                {{ "%.0f"|format(opp.confidence * 100) }}%
                            </span>
                        </td>
                        <td style="font-size: 0.9em;">
                            {% if opp.news_catalyst and opp.news_catalyst != 'Technical setup' %}
                                <span class="catalyst-badge">NEWS</span> {{ opp.news_catalyst[:60] }}...
                            {% else %}
                                {{ opp.reason }}
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p>Scanner is analyzing catalysts and market conditions...</p>
            {% endif %}
        </div>
        
        {% if trading_status and positions %}
        <div class="status-card">
            <h2>Current Positions</h2>
            <table class="positions-table">
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Quantity</th>
                        <th>Entry Price</th>
                        <th>Market Value</th>
                        <th>Unrealized P/L</th>
                        <th>% Change</th>
                    </tr>
                </thead>
                <tbody>
                    {% for pos in positions %}
                    <tr>
                        <td><strong>{{ pos.symbol }}</strong></td>
                        <td>{{ pos.qty }}</td>
                        <td>${{ "%.2f"|format(pos.avg_entry_price) }}</td>
                        <td>${{ "%.2f"|format(pos.market_value) }}</td>
                        <td class="{{ 'profit' if pos.unrealized_pl >= 0 else 'loss' }}">
                            ${{ "%.2f"|format(pos.unrealized_pl) }}
                        </td>
                        <td class="{{ 'profit' if pos.unrealized_pl >= 0 else 'loss' }}">
                            {{ "%.2f"|format((pos.unrealized_pl / (pos.avg_entry_price * pos.qty)) * 100) }}%
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
        
        <div class="status-card">
            <h2>📊 Strategy Overview</h2>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <h3>Multi-Stage Catalyst Filtering</h3>
                    <ul>
                        <li>📈 Stage 1: Top 100 active stocks</li>
                        <li>📰 Stage 2: Filter by news catalysts</li>
                        <li>🎯 Stage 3: Technical confirmation</li>
                        <li>💎 Result: Top 5 high-conviction trades</li>
                    </ul>
                </div>
                <div>
                    <h3>Community Impact Goals</h3>
                    <ul>
                        <li>🎓 Education: Fund scholarships</li>
                        <li>🏥 Healthcare: Support clinics</li>
                        <li>🏠 Housing: Assistance programs</li>
                        <li>💼 Business: Micro-loans</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def dashboard():
    """Main dashboard with all services integrated"""
    return render_template_string(DASHBOARD_HTML,
        trading_status=trading_client is not None,
        scanner_active=bool(app.extensions.get('scanner_service')),
        news_active=bool(app.extensions.get('news_service')),
        environment=os.getenv('ENVIRONMENT', 'development'),
        last_update=last_update.strftime('%Y-%m-%d %H:%M:%S') if last_update else 'Never',
        account=account_info,
        positions=positions_cache,
        opportunities=scanner_opportunities[:5],
        news_headlines=news_headlines
    )

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'trading': trading_client is not None,
            'scanner': bool(app.extensions.get('scanner_service')),
            'news': bool(app.extensions.get('news_service'))
        },
        'environment': os.getenv('ENVIRONMENT', 'development')
    })

@app.route('/api/execute_trade', methods=['POST'])
def execute_trade():
    """Execute a trade based on scanner recommendation"""
    if not trading_client:
        return jsonify({'error': 'Trading client not initialized'}), 503
    
    data = request.json
    symbol = data.get('symbol')
    action = data.get('action')
    quantity = data.get('quantity', 1)
    
    try:
        order_request = MarketOrderRequest(
            symbol=symbol,
            qty=quantity,
            side=OrderSide.BUY if action == 'BUY' else OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )
        
        order = trading_client.submit_order(order_request)
        
        return jsonify({
            'status': 'success',
            'order_id': order.id,
            'symbol': order.symbol,
            'quantity': order.qty,
            'side': order.side
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def background_updater():
    """Background thread to update all services periodically"""
    while True:
        try:
            # Update trading data
            if trading_client:
                update_positions()
                account = trading_client.get_account()
                account_info.update({
                    'status': account.status,
                    'buying_power': float(account.buying_power),
                    'portfolio_value': float(account.portfolio_value),
                    'cash': float(account.cash),
                    'equity': float(account.equity)
                })
            
            # Update scanner results
            update_scanner_results()
            
            # Update news headlines
            update_news_headlines()
            
            threading.Event().wait(60)  # Update every minute
            
        except Exception as e:
            logger.error(f"Background updater error: {e}")
            threading.Event().wait(60)

# Initialize everything on startup
if __name__ == '__main__':
    logger.info("🚀 Starting Catalyst Trading System - Full Integration...")
    
    # Initialize trading
    if initialize_trading():
        logger.info("✅ Trading initialized successfully")
        update_positions()
    else:
        logger.warning("⚠️ Running without trading connection")
    
    # Initialize news service
    try:
        from news_service import init_news_service
        news_service = init_news_service(app)
        app.extensions['news_service'] = news_service
        logger.info("✅ News service integrated")
    except Exception as e:
        logger.error(f"News service initialization failed: {e}")
    
    # Initialize scanner service
    try:
        scanner_service = init_scanner(app)
        app.extensions['scanner_service'] = scanner_service
        logger.info("✅ Scanner service integrated")
    except Exception as e:
        logger.error(f"Scanner service initialization failed: {e}")
    
    # Start background updater
    updater_thread = threading.Thread(target=background_updater, daemon=True)
    updater_thread.start()
    
    # Start Flask
    port = int(os.getenv('PORT', 8080))
    logger.info(f"🎯 Catalyst Trading System ready on port {port}")
    logger.info("📊 Multi-stage filtering: 100 stocks → 20 catalysts → 5 opportunities")
    logger.info("💚 Trading for community impact!")
    
    app.run(host='0.0.0.0', port=port, debug=False)
