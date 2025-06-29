#!/usr/bin/env python3
"""
Catalyst Trading System
Name of file: verify_trading_config.py
Version: 1.0.0
Last Updated: 2025-06-30
REVISION HISTORY:
  - v1.0.0 (2025-06-30) - Quick verification of API connections
"""

import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import requests

def verify_apis():
    """Verify all API connections are working"""
    
    print("🔍 Catalyst Trading System - API Verification")
    print("=" * 50)
    
    results = {}
    
    # Test Alpaca
    try:
        print("\n📊 Testing Alpaca Paper Trading...")
        trading_client = TradingClient(
            os.getenv('ALPACA_API_KEY', 'PK8ZTV60LQ83FALFQ2G4'),
            os.getenv('ALPACA_SECRET_KEY', '6VvdVlR9h5KcH9BXxLIa4XqHlX8VS0AKbWQcZood'),
            paper=True
        )
        account = trading_client.get_account()
        print(f"✅ Alpaca Connected!")
        print(f"   - Account Status: {account.status}")
        print(f"   - Buying Power: ${account.buying_power}")
        print(f"   - Portfolio Value: ${account.portfolio_value}")
        results['alpaca'] = True
    except Exception as e:
        print(f"❌ Alpaca Failed: {e}")
        results['alpaca'] = False
    
    # Test Alpha Vantage
    try:
        print("\n📈 Testing Alpha Vantage...")
        api_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'HOHN6L2KWKY20TOL')
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey={api_key}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and 'Global Quote' in response.json():
            print("✅ Alpha Vantage Connected!")
            results['alpha_vantage'] = True
        else:
            print("❌ Alpha Vantage Failed")
            results['alpha_vantage'] = False
    except Exception as e:
        print(f"❌ Alpha Vantage Failed: {e}")
        results['alpha_vantage'] = False
    
    # Test Twelve Data
    try:
        print("\n📊 Testing Twelve Data...")
        api_key = os.getenv('TWELVE_DATA_API_KEY', 'e1038aa6fb3940f2a92c6331f501d02e')
        url = f"https://api.twelvedata.com/quote?symbol=AAPL&apikey={api_key}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("✅ Twelve Data Connected!")
            results['twelve_data'] = True
        else:
            print("❌ Twelve Data Failed")
            results['twelve_data'] = False
    except Exception as e:
        print(f"❌ Twelve Data Failed: {e}")
        results['twelve_data'] = False
    
    # Test NewsAPI
    try:
        print("\n📰 Testing NewsAPI...")
        api_key = os.getenv('NEWSAPI_KEY', 'd2fcbdb11c134ebb9ba7da25c7e727a7')
        url = f"https://newsapi.org/v2/top-headlines?sources=bloomberg&apiKey={api_key}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("✅ NewsAPI Connected!")
            results['newsapi'] = True
        else:
            print("❌ NewsAPI Failed")
            results['newsapi'] = False
    except Exception as e:
        print(f"❌ NewsAPI Failed: {e}")
        results['newsapi'] = False
    
    # Test OpenAI (just verify key format, don't make actual call to save credits)
    try:
        print("\n🤖 Testing OpenAI...")
        api_key = os.getenv('OPENAI_API_KEY', 'sk-proj-...')
        if api_key and api_key.startswith('sk-'):
            print("✅ OpenAI API Key Format Valid!")
            results['openai'] = True
        else:
            print("❌ OpenAI API Key Invalid Format")
            results['openai'] = False
    except Exception as e:
        print(f"❌ OpenAI Failed: {e}")
        results['openai'] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 API Status Summary:")
    for api, status in results.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {api.replace('_', ' ').title()}")
    
    all_critical_working = results.get('alpaca', False)
    if all_critical_working:
        print("\n🎉 Critical APIs working! Ready for paper trading!")
    else:
        print("\n⚠️ Fix critical API issues before deploying!")
    
    return results

if __name__ == "__main__":
    # Test with environment variables
    print("Testing with environment variables...\n")
    verify_apis()
    
    # Create a simple test trade function
    print("\n\n🧪 Test Paper Trade Function:")
    print("=" * 50)
    
    try:
        client = TradingClient(
            os.getenv('ALPACA_API_KEY', 'PK8ZTV60LQ83FALFQ2G4'),
            os.getenv('ALPACA_SECRET_KEY', '6VvdVlR9h5KcH9BXxLIa4XqHlX8VS0AKbWQcZood'),
            paper=True
        )
        
        # Get current positions
        positions = client.get_all_positions()
        print(f"\n📊 Current Positions: {len(positions)}")
        for position in positions:
            print(f"  - {position.symbol}: {position.qty} shares @ ${position.avg_entry_price}")
        
        print("\n✅ Paper trading connection verified!")
        
    except Exception as e:
        print(f"\n❌ Paper trading test failed: {e}")
