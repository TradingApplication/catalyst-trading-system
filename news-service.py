#!/usr/bin/env python3
"""
Catalyst Trading System
Name of Service: NEWS COLLECTION SERVICE - SIMPLIFIED
Version: 1.0.0
Last Updated: 2025-06-30
Purpose: Collect news catalysts for trading opportunities

REVISION HISTORY:
v1.0.0 (2025-06-30) - Simplified for DigitalOcean deployment
- NewsAPI integration (we have the key)
- Alpha Vantage news (we have the key)
- Focus on actionable catalysts
- Integrated with scanner service
"""

import os
import json
import time
import sqlite3
import logging
import requests
from datetime import datetime, timedelta
from flask import Flask, Blueprint, jsonify, request
from typing import Dict, List, Optional
import hashlib
import threading

# Create Flask Blueprint
news_bp = Blueprint('news', __name__)

class SimplifiedNewsService:
    """
    Simplified news service focused on trading catalysts
    """
    
    def __init__(self, app=None):
        self.app = app
        self.setup_logging()
        
        # API Keys from environment
        self.api_keys = {
            'newsapi': os.getenv('NEWSAPI_KEY'),
            'alphavantage': os.getenv('ALPHA_VANTAGE_API_KEY')
        }
        
        # Verify we have at least one news source
        self.has_news_source = bool(self.api_keys['newsapi'] or self.api_keys['alphavantage'])
        
        if not self.has_news_source:
            self.logger.warning("⚠️ No news API keys configured")
        else:
            self.logger.info("✅ News service initialized with available APIs")
        
        # Database
        self.db_path = '/tmp/trading_system.db'
        self._init_database()
        
        # Cache for recent news
        self.news_cache = {}
        self.cache_duration = 300  # 5 minutes
        
        # High-impact keywords for catalyst detection
        self.catalyst_keywords = {
            'high_impact': ['earnings', 'fda', 'merger', 'acquisition', 'bankruptcy', 
                          'sec', 'investigation', 'recall', 'guidance'],
            'medium_impact': ['upgrade', 'downgrade', 'analyst', 'partnership', 
                            'contract', 'expansion', 'layoffs', 'restructuring'],
            'product': ['launch', 'release', 'unveil', 'announce', 'introduce']
        }
        
    def setup_logging(self):
        """Setup logging configuration"""
        self.logger = logging.getLogger('news_service')
        self.logger.setLevel(logging.INFO)
        
        os.makedirs('/tmp/logs', exist_ok=True)
        
        fh = logging.FileHandler('/tmp/logs/news_service.log')
        fh.setLevel(logging.INFO)
        
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def _init_database(self):
        """Initialize database for news storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS news_simplified (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    news_id TEXT UNIQUE NOT NULL,
                    symbol TEXT,
                    headline TEXT NOT NULL,
                    source TEXT NOT NULL,
                    published_timestamp TIMESTAMP NOT NULL,
                    collected_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    keywords JSON,
                    is_breaking BOOLEAN DEFAULT FALSE,
                    is_pre_market BOOLEAN DEFAULT FALSE,
                    impact_score REAL DEFAULT 0,
                    url TEXT
                )
            ''')
            
            # Create index for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_news_symbol_time 
                ON news_simplified(symbol, published_timestamp DESC)
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Database init error: {e}")
    
    def generate_news_id(self, headline: str, source: str) -> str:
        """Generate unique ID for news article"""
        content = f"{headline}_{source}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def is_pre_market(self, timestamp: datetime) -> bool:
        """Check if news was published during pre-market hours"""
        hour = timestamp.hour
        # Assuming EST timezone (UTC-5)
        est_hour = (hour - 5) % 24
        return 4 <= est_hour < 9.5
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract catalyst keywords from text"""
        found_keywords = []
        text_lower = text.lower()
        
        for impact_level, keywords in self.catalyst_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_keywords.append(keyword)
        
        return list(set(found_keywords))
    
    def calculate_impact_score(self, headline: str, keywords: List[str], 
                             is_breaking: bool, is_pre_market: bool) -> float:
        """Calculate impact score for news (0-1)"""
        score = 0.0
        
        # Keyword impact
        for keyword in keywords:
            if keyword in self.catalyst_keywords['high_impact']:
                score += 0.3
            elif keyword in self.catalyst_keywords['medium_impact']:
                score += 0.15
            elif keyword in self.catalyst_keywords['product']:
                score += 0.1
        
        # Breaking news boost
        if is_breaking or 'breaking' in headline.lower():
            score *= 1.5
        
        # Pre-market boost
        if is_pre_market:
            score *= 1.3
        
        return min(score, 1.0)  # Cap at 1.0
    
    def fetch_newsapi(self, symbol: str) -> List[Dict]:
        """Fetch news from NewsAPI"""
        if not self.api_keys['newsapi']:
            return []
        
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                'apiKey': self.api_keys['newsapi'],
                'q': f'"{symbol}" stock',
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 10,
                'from': (datetime.now() - timedelta(hours=24)).isoformat()
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                news_items = []
                
                for article in data.get('articles', []):
                    published = datetime.fromisoformat(
                        article['publishedAt'].replace('Z', '+00:00')
                    )
                    
                    headline = article.get('title', '')
                    keywords = self.extract_keywords(headline)
                    is_pre_market_news = self.is_pre_market(published)
                    
                    news_items.append({
                        'symbol': symbol,
                        'headline': headline,
                        'source': 'NewsAPI',
                        'published': published,
                        'keywords': keywords,
                        'is_breaking': False,
                        'is_pre_market': is_pre_market_news,
                        'impact_score': self.calculate_impact_score(
                            headline, keywords, False, is_pre_market_news
                        ),
                        'url': article.get('url', '')
                    })
                
                return news_items
                
        except Exception as e:
            self.logger.error(f"NewsAPI error for {symbol}: {e}")
        
        return []
    
    def fetch_alphavantage(self, symbol: str) -> List[Dict]:
        """Fetch news from Alpha Vantage"""
        if not self.api_keys['alphavantage']:
            return []
        
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': symbol,
                'apikey': self.api_keys['alphavantage']
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                news_items = []
                
                for article in data.get('feed', [])[:10]:  # Limit to 10
                    published = datetime.strptime(
                        article['time_published'], 
                        '%Y%m%dT%H%M%S'
                    )
                    
                    headline = article.get('title', '')
                    keywords = self.extract_keywords(headline)
                    is_pre_market_news = self.is_pre_market(published)
                    
                    news_items.append({
                        'symbol': symbol,
                        'headline': headline,
                        'source': 'AlphaVantage',
                        'published': published,
                        'keywords': keywords,
                        'is_breaking': False,
                        'is_pre_market': is_pre_market_news,
                        'impact_score': self.calculate_impact_score(
                            headline, keywords, False, is_pre_market_news
                        ),
                        'url': article.get('url', '')
                    })
                
                return news_items
                
        except Exception as e:
            self.logger.error(f"AlphaVantage error for {symbol}: {e}")
        
        return []
    
    def collect_news(self, symbol: str) -> List[Dict]:
        """Collect news from all available sources"""
        # Check cache first
        cache_key = f"{symbol}_{datetime.now().strftime('%Y%m%d%H')}"
        if cache_key in self.news_cache:
            cache_time, cached_news = self.news_cache[cache_key]
            if (datetime.now() - cache_time).seconds < self.cache_duration:
                return cached_news
        
        all_news = []
        
        # Collect from available sources
        if self.api_keys['newsapi']:
            all_news.extend(self.fetch_newsapi(symbol))
        
        if self.api_keys['alphavantage']:
            all_news.extend(self.fetch_alphavantage(symbol))
        
        # Sort by impact score
        all_news.sort(key=lambda x: x['impact_score'], reverse=True)
        
        # Cache results
        self.news_cache[cache_key] = (datetime.now(), all_news)
        
        # Save to database
        self.save_news_items(all_news)
        
        return all_news
    
    def save_news_items(self, news_items: List[Dict]):
        """Save news items to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for item in news_items:
                news_id = self.generate_news_id(item['headline'], item['source'])
                
                cursor.execute('''
                    INSERT OR REPLACE INTO news_simplified
                    (news_id, symbol, headline, source, published_timestamp,
                     keywords, is_breaking, is_pre_market, impact_score, url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    news_id,
                    item['symbol'],
                    item['headline'],
                    item['source'],
                    item['published'],
                    json.dumps(item['keywords']),
                    item['is_breaking'],
                    item['is_pre_market'],
                    item['impact_score'],
                    item['url']
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error saving news: {e}")
    
    def search_news(self, params: Dict) -> List[Dict]:
        """Search news by parameters"""
        try:
            symbol = params.get('symbol')
            hours = params.get('hours', 24)
            
            if symbol:
                # Collect fresh news for the symbol
                fresh_news = self.collect_news(symbol)
                
                # Filter by time
                cutoff = datetime.now() - timedelta(hours=hours)
                filtered = [n for n in fresh_news if n['published'] > cutoff]
                
                # Format for response
                results = []
                for news in filtered:
                    results.append({
                        'symbol': news['symbol'],
                        'headline': news['headline'],
                        'source': news['source'],
                        'published': news['published'].isoformat(),
                        'keywords': news['keywords'],
                        'breaking': news['is_breaking'],
                        'pre_market': news['is_pre_market'],
                        'impact_score': news['impact_score'],
                        'url': news['url']
                    })
                
                return results
            
        except Exception as e:
            self.logger.error(f"Search error: {e}")
        
        return []

# Initialize news service
news_service = None

@news_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'news_simplified',
        'version': '1.0.0',
        'apis_configured': bool(news_service and news_service.has_news_source)
    })

@news_bp.route('/search_news', methods=['GET'])
def search_news():
    """Search news for a symbol"""
    if not news_service:
        return jsonify({'error': 'News service not initialized'}), 503
    
    params = {
        'symbol': request.args.get('symbol'),
        'hours': request.args.get('hours', 24, type=int)
    }
    
    if not params['symbol']:
        return jsonify({'error': 'Symbol parameter required'}), 400
    
    results = news_service.search_news(params)
    
    return jsonify({
        'count': len(results),
        'results': results,
        'query_params': params,
        'timestamp': datetime.now().isoformat()
    })

@news_bp.route('/collect_news', methods=['POST'])
def collect_news():
    """Manually trigger news collection"""
    if not news_service:
        return jsonify({'error': 'News service not initialized'}), 503
    
    data = request.json or {}
    symbols = data.get('symbols', [])
    
    if not symbols:
        return jsonify({'error': 'Symbols list required'}), 400
    
    results = {}
    for symbol in symbols[:10]:  # Limit to 10 symbols
        news_items = news_service.collect_news(symbol)
        results[symbol] = len(news_items)
    
    return jsonify({
        'status': 'success',
        'symbols_processed': len(results),
        'results': results,
        'timestamp': datetime.now().isoformat()
    })

def init_news_service(app):
    """Initialize news service with Flask app"""
    global news_service
    news_service = SimplifiedNewsService(app)
    app.register_blueprint(news_bp, url_prefix='/news')
    
    logging.info("✅ News service initialized")
    
    return news_service

# Standalone mode
if __name__ == '__main__':
    app = Flask(__name__)
    init_news_service(app)
    app.run(host='0.0.0.0', port=5008, debug=False)
