#!/usr/bin/env python3
"""
Catalyst Trading System
Name of Service: COMMUNITY PROFIT SCANNER WITH NEWS INTEGRATION
Version: 4.0.0
Last Updated: 2025-06-30
Purpose: Find profitable trading opportunities using news catalysts for community impact

REVISION HISTORY:
v4.0.0 (2025-06-30) - Full news integration for catalyst-based trading
- Integrated news service for catalyst filtering
- Multi-stage filtering: 100 → 20 (news) → 5 (technical)
- Pre-market focus for maximum opportunity
- Community impact scoring with news weight
"""

import os
import json
import time
import sqlite3
import logging
import requests
from datetime import datetime, timedelta
from flask import Flask, Blueprint, jsonify, request
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import threading

# Import Alpaca for real market data
try:
    from alpaca.data import StockHistoricalDataClient, StockBarsRequest, TimeFrame
    from alpaca.trading.client import TradingClient
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False

# Import technical analysis
try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

class CommunityProfitScanner:
    """
    Scanner that combines news catalysts with technical analysis for community profit
    """
    
    def __init__(self, app=None):
        self.app = app
        self.setup_logging()
        
        # Initialize Alpaca clients
        api_key = os.getenv('ALPACA_API_KEY')
        secret_key = os.getenv('ALPACA_SECRET_KEY')
        
        if ALPACA_AVAILABLE and api_key and secret_key:
            self.data_client = StockHistoricalDataClient(api_key, secret_key)
            self.trading_client = TradingClient(api_key, secret_key, paper=True)
            self.logger.info("✅ Connected to Alpaca for market data")
        else:
            self.data_client = None
            self.trading_client = None
            self.logger.warning("⚠️ Running without Alpaca connection")
        
        # News service integration
        self.news_service_url = "http://localhost:5008"
        self.news_service_available = self._check_news_service()
        
        # Multi-stage scanning parameters
        self.scan_params = {
            # Stage 1: Initial universe
            'initial_universe_size': 100,    # Start with top 100 active
            
            # Stage 2: News catalyst filter
            'catalyst_filter_size': 20,      # Narrow to 20 with news
            'min_news_score': 0.3,           # Minimum news relevance
            'breaking_news_boost': 2.0,      # Double score for breaking
            'pre_market_boost': 1.5,         # 50% boost for pre-market news
            
            # Stage 3: Technical confirmation
            'final_selection_size': 5,       # Final 5 picks
            'min_price': 5.0,               # Quality stocks
            'max_price': 500.0,             # Accessible range
            'min_volume': 500000,           # Liquidity threshold
            'min_relative_volume': 1.5,     # 50% above average
            
            # News catalyst keywords that matter
            'high_impact_keywords': ['earnings', 'fda', 'merger', 'acquisition', 
                                   'bankruptcy', 'guidance', 'analyst'],
            'medium_impact_keywords': ['product', 'partnership', 'expansion', 
                                     'contract', 'revenue'],
            
            # Risk management
            'stop_loss': 0.02,              # 2% stop loss
            'take_profit': 0.05,            # 5% profit target
        }
        
        # Cache for scan results
        self.scan_cache = {
            'timestamp': None,
            'universe': [],
            'catalyst_filtered': [],
            'final_picks': [],
            'news_data': {}
        }
        
        # Extended universe for news-driven opportunities
        self.scan_universe = [
            # Mega caps (stable, high volume)
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'BRK.B',
            
            # Large caps (good for news reactions)
            'JPM', 'V', 'JNJ', 'WMT', 'PG', 'MA', 'HD', 'DIS', 'BAC', 'XOM',
            'CVX', 'ABBV', 'PFE', 'KO', 'PEP', 'MRK', 'TMO', 'CSCO', 'VZ', 'INTC',
            
            # High beta tech (big moves on news)
            'AMD', 'ADBE', 'CRM', 'NFLX', 'PYPL', 'QCOM', 'TXN', 'AVGO', 'ORCL',
            'NOW', 'UBER', 'ABNB', 'SQ', 'SHOP', 'SNAP', 'PINS', 'ROKU', 'ZM',
            
            # Biotech (FDA news plays)
            'GILD', 'AMGN', 'VRTX', 'REGN', 'MRNA', 'BIIB', 'ILMN',
            
            # Financial (rate sensitive)
            'GS', 'MS', 'C', 'WFC', 'AXP', 'SCHW', 'BLK', 'SPGI',
            
            # Retail (earnings plays)
            'TGT', 'COST', 'NKE', 'SBUX', 'MCD', 'LOW', 'CVS', 'AMZN',
            
            # Energy (commodity news)
            'COP', 'SLB', 'EOG', 'PSX', 'MPC', 'VLO',
            
            # Popular retail trader stocks
            'GME', 'AMC', 'BBBY', 'BB', 'PLTR', 'SOFI', 'RIVN', 'LCID'
        ]
        
        # Database path
        self.db_path = '/tmp/trading_system.db'
        self._init_database()
        
    def setup_logging(self):
        """Setup logging configuration"""
        self.logger = logging.getLogger('catalyst_scanner')
        self.logger.setLevel(logging.INFO)
        
        os.makedirs('/tmp/logs', exist_ok=True)
        
        fh = logging.FileHandler('/tmp/logs/catalyst_scanner.log')
        fh.setLevel(logging.INFO)
        
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        
    def _check_news_service(self) -> bool:
        """Check if news service is available"""
        try:
            # For DigitalOcean deployment, news might not be available yet
            # So we'll work without it initially
            return False  # Disable for now, enable when news service is deployed
            
            response = requests.get(f"{self.news_service_url}/health", timeout=2)
            if response.status_code == 200:
                self.logger.info("✅ News service connected")
                return True
        except:
            pass
        
        self.logger.warning("⚠️ News service not available - using technical analysis only")
        return False
        
    def _init_database(self):
        """Initialize database for scan results"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scan_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    symbol TEXT NOT NULL,
                    action TEXT NOT NULL,
                    entry_price REAL,
                    stop_loss REAL,
                    take_profit REAL,
                    confidence REAL,
                    volume INTEGER,
                    relative_volume REAL,
                    price_change REAL,
                    rsi REAL,
                    pattern TEXT,
                    community_score REAL,
                    news_score REAL,
                    news_catalyst TEXT,
                    reason TEXT,
                    status TEXT DEFAULT 'pending'
                )
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info("✅ Database initialized")
            
        except Exception as e:
            self.logger.error(f"Database init error: {e}")
    
    def get_market_movers(self) -> List[str]:
        """Get today's most active stocks"""
        # For now, return our predefined universe
        # In production, this would query real-time data
        return self.scan_universe[:self.scan_params['initial_universe_size']]
    
    def get_news_catalysts(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get news catalysts for symbols"""
        if not self.news_service_available:
            # Return empty catalysts if news service unavailable
            return {}
        
        try:
            # Query news service for each symbol
            news_data = {}
            
            for symbol in symbols:
                response = requests.get(
                    f"{self.news_service_url}/search_news",
                    params={
                        'symbol': symbol,
                        'hours': 24,
                        'breaking_only': False
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('results'):
                        news_data[symbol] = self._analyze_news_catalyst(symbol, data['results'])
            
            return news_data
            
        except Exception as e:
            self.logger.error(f"Error getting news catalysts: {e}")
            return {}
    
    def _analyze_news_catalyst(self, symbol: str, news_items: List[Dict]) -> Dict:
        """Analyze news items to create catalyst score"""
        if not news_items:
            return {'score': 0, 'catalyst': None, 'count': 0}
        
        total_score = 0
        best_catalyst = None
        
        for news in news_items:
            score = 0
            
            # Score based on keywords
            keywords = news.get('keywords', [])
            for keyword in keywords:
                if keyword in self.scan_params['high_impact_keywords']:
                    score += 0.3
                elif keyword in self.scan_params['medium_impact_keywords']:
                    score += 0.15
            
            # Boost for breaking news
            if news.get('breaking', False):
                score *= self.scan_params['breaking_news_boost']
            
            # Boost for pre-market news
            if news.get('pre_market', False):
                score *= self.scan_params['pre_market_boost']
            
            # Time decay (newer = better)
            try:
                published = datetime.fromisoformat(news.get('published', ''))
                hours_old = (datetime.now() - published).total_seconds() / 3600
                time_factor = max(0, 1 - (hours_old / 24))  # Linear decay over 24h
                score *= time_factor
            except:
                pass
            
            total_score += score
            
            if score > 0 and not best_catalyst:
                best_catalyst = {
                    'headline': news.get('headline', ''),
                    'keywords': keywords,
                    'pre_market': news.get('pre_market', False),
                    'breaking': news.get('breaking', False)
                }
        
        return {
            'score': min(total_score, 1.0),  # Cap at 1.0
            'catalyst': best_catalyst,
            'count': len(news_items)
        }
    
    def calculate_technical_indicators(self, symbol: str, bars: pd.DataFrame) -> Dict:
        """Calculate technical indicators for a symbol"""
        if not PANDAS_AVAILABLE or bars.empty:
            return {}
        
        try:
            indicators = {}
            
            # Price and volume
            current_price = bars['close'].iloc[-1]
            indicators['price'] = current_price
            indicators['volume'] = bars['volume'].iloc[-1]
            
            # Moving averages
            indicators['sma_20'] = bars['close'].rolling(window=20).mean().iloc[-1]
            indicators['sma_50'] = bars['close'].rolling(window=50).mean().iloc[-1]
            indicators['above_sma20'] = current_price > indicators['sma_20']
            
            # Volume analysis
            indicators['avg_volume'] = bars['volume'].rolling(window=20).mean().iloc[-1]
            indicators['rel_volume'] = indicators['volume'] / indicators['avg_volume']
            
            # Price change
            indicators['change_pct'] = ((current_price - bars['close'].iloc[-2]) / bars['close'].iloc[-2]) * 100
            
            # RSI
            delta = bars['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators['rsi'] = 100 - (100 / (1 + rs)).iloc[-1]
            
            # Support and Resistance
            indicators['support'] = bars['low'].rolling(window=20).min().iloc[-1]
            indicators['resistance'] = bars['high'].rolling(window=20).max().iloc[-1]
            
            # Volatility (for risk assessment)
            indicators['volatility'] = bars['close'].pct_change().rolling(window=20).std().iloc[-1]
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"Error calculating indicators for {symbol}: {e}")
            return {}
    
    def get_market_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get recent market data for a symbol"""
        if not self.data_client:
            return None
            
        try:
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Day,
                start=datetime.now() - timedelta(days=50)
            )
            
            bars = self.data_client.get_stock_bars(request)
            df = bars.df
            
            if not df.empty:
                return df
                
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}")
            
        return None
    
    def calculate_community_score(self, symbol: str, indicators: Dict, news_score: float) -> float:
        """
        Calculate community impact score combining news catalysts and technical setup
        """
        score = 0.0
        
        # News catalyst score (0-40 points) - HIGHEST WEIGHT
        score += news_score * 40
        
        # Momentum score (0-20 points)
        if indicators.get('rel_volume', 0) > self.scan_params['min_relative_volume']:
            score += 10
        if abs(indicators.get('change_pct', 0)) > 1.0:
            score += 10
            
        # Technical setup score (0-30 points)
        rsi = indicators.get('rsi', 50)
        if 30 <= rsi <= 35:  # Oversold
            score += 30
        elif 35 < rsi <= 45:  # Approaching oversold
            score += 20
        elif 45 < rsi <= 65:  # Neutral
            score += 10
            
        # Trend alignment (0-10 points)
        if indicators.get('above_sma20', False):
            score += 10
        
        return score / 100.0
    
    def scan_for_opportunities(self) -> List[Dict]:
        """
        Multi-stage scan: Universe → News Filter → Technical Confirmation
        """
        # Check cache
        if self.scan_cache['timestamp']:
            cache_age = (datetime.now() - self.scan_cache['timestamp']).seconds
            if cache_age < 300:  # 5 minutes
                return self.scan_cache['final_picks']
        
        self.logger.info("🔍 Starting multi-stage catalyst scan...")
        
        # Stage 1: Get initial universe (top movers or predefined list)
        universe = self.get_market_movers()
        self.logger.info(f"Stage 1: Starting with {len(universe)} stocks")
        
        # Stage 2: Filter by news catalysts
        news_data = self.get_news_catalysts(universe)
        catalyst_stocks = []
        
        for symbol in universe:
            news_info = news_data.get(symbol, {'score': 0})
            if news_info['score'] >= self.scan_params['min_news_score']:
                catalyst_stocks.append({
                    'symbol': symbol,
                    'news_score': news_info['score'],
                    'catalyst': news_info.get('catalyst')
                })
        
        # Sort by news score and take top N
        catalyst_stocks.sort(key=lambda x: x['news_score'], reverse=True)
        catalyst_stocks = catalyst_stocks[:self.scan_params['catalyst_filter_size']]
        
        self.logger.info(f"Stage 2: {len(catalyst_stocks)} stocks with news catalysts")
        
        # Stage 3: Technical analysis on catalyst stocks
        opportunities = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {}
            
            for stock in catalyst_stocks:
                future = executor.submit(
                    self.analyze_catalyst_stock, 
                    stock['symbol'], 
                    stock['news_score'],
                    stock.get('catalyst')
                )
                futures[future] = stock['symbol']
            
            for future in futures:
                try:
                    result = future.result(timeout=10)
                    if result:
                        opportunities.append(result)
                except Exception as e:
                    symbol = futures[future]
                    self.logger.error(f"Error analyzing {symbol}: {e}")
        
        # Final selection: Sort by community score and take top 5
        opportunities.sort(key=lambda x: x['community_score'], reverse=True)
        final_picks = opportunities[:self.scan_params['final_selection_size']]
        
        # Update cache
        self.scan_cache['timestamp'] = datetime.now()
        self.scan_cache['universe'] = universe
        self.scan_cache['catalyst_filtered'] = catalyst_stocks
        self.scan_cache['final_picks'] = final_picks
        self.scan_cache['news_data'] = news_data
        
        # Save to database
        self.save_scan_results(final_picks)
        
        self.logger.info(f"✅ Scan complete: {len(final_picks)} opportunities found")
        
        return final_picks
    
    def analyze_catalyst_stock(self, symbol: str, news_score: float, catalyst: Dict) -> Optional[Dict]:
        """Analyze a stock with news catalyst"""
        try:
            # Get market data
            bars = self.get_market_data(symbol)
            if bars is None or bars.empty:
                return None
            
            # Calculate indicators
            indicators = self.calculate_technical_indicators(symbol, bars)
            if not indicators:
                return None
            
            # Calculate community score (news + technical)
            community_score = self.calculate_community_score(symbol, indicators, news_score)
            
            # Determine trade setup
            action, entry, stop, target, reason = self.determine_catalyst_trade(
                symbol, indicators, news_score, catalyst
            )
            
            if action:
                return {
                    'symbol': symbol,
                    'action': action,
                    'entry_price': entry,
                    'stop_loss': stop,
                    'take_profit': target,
                    'confidence': min(community_score + 0.2, 1.0),
                    'volume': indicators.get('volume', 0),
                    'relative_volume': indicators.get('rel_volume', 0),
                    'price_change': indicators.get('change_pct', 0),
                    'rsi': indicators.get('rsi', 0),
                    'pattern': 'catalyst',
                    'community_score': community_score,
                    'news_score': news_score,
                    'news_catalyst': catalyst.get('headline', 'Technical setup') if catalyst else 'Technical setup',
                    'reason': reason,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {e}")
            
        return None
    
    def determine_catalyst_trade(self, symbol: str, indicators: Dict, 
                               news_score: float, catalyst: Dict) -> Tuple:
        """Determine trade setup based on catalyst + technical"""
        price = indicators.get('price', 0)
        rsi = indicators.get('rsi', 50)
        change_pct = indicators.get('change_pct', 0)
        rel_volume = indicators.get('rel_volume', 1)
        
        # Strong catalyst + oversold = High conviction buy
        if news_score > 0.5 and rsi <= 35:
            entry = price
            stop = price * (1 - self.scan_params['stop_loss'])
            target = price * (1 + self.scan_params['take_profit'])
            catalyst_text = catalyst.get('headline', 'Strong catalyst')[:50] if catalyst else 'Technical oversold'
            reason = f"Strong catalyst + oversold RSI {rsi:.1f}: {catalyst_text}"
            return ('BUY', entry, stop, target, reason)
        
        # Moderate catalyst + good technical = Standard buy
        elif news_score > 0.3 and rsi <= 45 and rel_volume > 1.5:
            entry = price
            stop = price * (1 - self.scan_params['stop_loss'])
            target = price * (1 + self.scan_params['take_profit'])
            catalyst_text = catalyst.get('headline', 'News catalyst')[:50] if catalyst else 'Volume surge'
            reason = f"Catalyst + volume {rel_volume:.1f}x: {catalyst_text}"
            return ('BUY', entry, stop, target, reason)
        
        # Pure technical setup (when no news service)
        elif not self.news_service_available:
            if rsi <= 35 and indicators.get('above_sma20', False):
                entry = price
                stop = price * (1 - self.scan_params['stop_loss'])
                target = price * (1 + self.scan_params['take_profit'])
                reason = f"Oversold bounce - RSI {rsi:.1f}, above 20MA"
                return ('BUY', entry, stop, target, reason)
            elif change_pct >= 2 and rel_volume >= 2:
                entry = price
                stop = indicators.get('support', price * 0.98)
                target = price * (1 + self.scan_params['take_profit'])
                reason = f"Momentum breakout - {change_pct:.1f}% on {rel_volume:.1f}x volume"
                return ('BUY', entry, stop, target, reason)
        
        return (None, None, None, None, None)
    
    def save_scan_results(self, opportunities: List[Dict]):
        """Save scan results to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for opp in opportunities:
                cursor.execute('''
                    INSERT INTO scan_results 
                    (symbol, action, entry_price, stop_loss, take_profit, 
                     confidence, volume, relative_volume, price_change, 
                     rsi, pattern, community_score, news_score, news_catalyst, reason)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    opp['symbol'], opp['action'], opp['entry_price'],
                    opp['stop_loss'], opp['take_profit'], opp['confidence'],
                    opp['volume'], opp['relative_volume'], opp['price_change'],
                    opp['rsi'], opp['pattern'], opp['community_score'],
                    opp.get('news_score', 0), opp.get('news_catalyst', ''),
                    opp['reason']
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error saving scan results: {e}")

# Flask Blueprint for integration
scanner_bp = Blueprint('scanner', __name__)
scanner_service = None

@scanner_bp.route('/scan', methods=['GET'])
def run_scan():
    """Run market scan and return opportunities"""
    if not scanner_service:
        return jsonify({'error': 'Scanner service not initialized'}), 503
        
    try:
        opportunities = scanner_service.scan_for_opportunities()
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'count': len(opportunities),
            'opportunities': opportunities,
            'news_service': scanner_service.news_service_available
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scanner_bp.route('/scan/history', methods=['GET'])
def get_scan_history():
    """Get historical scan results"""
    try:
        conn = sqlite3.connect('/tmp/trading_system.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM scan_results 
            ORDER BY timestamp DESC 
            LIMIT 100
        ''')
        
        columns = [desc[0] for desc in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
            
        conn.close()
        
        return jsonify({
            'status': 'success',
            'count': len(results),
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scanner_bp.route('/scan/stats', methods=['GET'])
def get_scan_stats():
    """Get scanning statistics"""
    if not scanner_service:
        return jsonify({'error': 'Scanner service not initialized'}), 503
        
    cache = scanner_service.scan_cache
    
    return jsonify({
        'status': 'success',
        'last_scan': cache['timestamp'].isoformat() if cache['timestamp'] else None,
        'opportunities_found': len(cache.get('final_picks', [])),
        'catalyst_stocks': len(cache.get('catalyst_filtered', [])),
        'universe_size': len(cache.get('universe', [])),
        'news_service_available': scanner_service.news_service_available,
        'scan_params': scanner_service.scan_params
    })

def init_scanner(app):
    """Initialize scanner service with Flask app"""
    global scanner_service
    scanner_service = CommunityProfitScanner(app)
    app.register_blueprint(scanner_bp, url_prefix='/scanner')
    
    # Start background scanning thread
    def background_scanner():
        while True:
            try:
                # More frequent scans during market hours
                current_hour = datetime.now().hour
                if 9 <= current_hour <= 16:  # Market hours (adjust for timezone)
                    scan_interval = 300  # 5 minutes
                else:
                    scan_interval = 900  # 15 minutes
                
                scanner_service.scan_for_opportunities()
                time.sleep(scan_interval)
            except Exception as e:
                logging.error(f"Background scan error: {e}")
                time.sleep(60)
    
    scanner_thread = threading.Thread(target=background_scanner, daemon=True)
    scanner_thread.start()
    
    logging.info("✅ Catalyst scanner service initialized")
    
    return scanner_service

# Standalone mode
if __name__ == '__main__':
    app = Flask(__name__)
    init_scanner(app)
    app.run(host='0.0.0.0', port=5002, debug=False)
