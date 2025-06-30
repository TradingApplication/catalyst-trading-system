#!/usr/bin/env python3
"""
Test Alpaca Connection
This script tests the Alpaca API connection using environment variables
"""

import os
import sys

print("🔍 Testing Alpaca Connection")
print("=" * 50)

# First, check what environment variables are available
print("\n📋 Checking Environment Variables:")
env_vars = [
    'ALPACA_API_KEY',
    'ALPACA_SECRET_KEY', 
    'ALPACA_BASE_URL',
    'ALPACA_PAPER_API_KEY',
    'ALPACA_PAPER_API_SECRET',
    'ALPACA_PAPER_BASE_URL'
]

found_vars = {}
for var in env_vars:
    value = os.getenv(var)
    if value:
        # Show first 10 chars for security
        masked = value[:10] + '...' if len(value) > 10 else value
        print(f"✅ {var}: {masked}")
        found_vars[var] = value
    else:
        print(f"❌ {var}: Not found")

# Try to import alpaca-py
print("\n📦 Testing Alpaca Import:")
try:
    from alpaca.trading.client import TradingClient
    print("✅ alpaca.trading.client imported successfully")
except ImportError as e:
    print(f"❌ Failed to import alpaca-py: {e}")
    print("   Run: pip install alpaca-py")
    sys.exit(1)

# Test connection with different configurations
print("\n🔌 Testing Connections:")
print("-" * 30)

# Configuration 1: Using ALPACA_API_KEY/SECRET
api_key = os.getenv('ALPACA_API_KEY')
secret_key = os.getenv('ALPACA_SECRET_KEY')
base_url = os.getenv('ALPACA_BASE_URL')

if api_key and secret_key:
    print("\n1️⃣ Testing with ALPACA_API_KEY/SECRET:")
    try:
        # Test without base_url (paper=True should handle it)
        print("   Attempting connection with paper=True...")
        client = TradingClient(api_key, secret_key, paper=True)
        account = client.get_account()
        print(f"   ✅ SUCCESS! Connected to Alpaca")
        print(f"   - Account Status: {account.status}")
        print(f"   - Buying Power: ${float(account.buying_power):,.2f}")
        print(f"   - Portfolio Value: ${float(account.portfolio_value):,.2f}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        
        # If base_url is set, try with it
        if base_url:
            print(f"\n   Retrying with base_url: {base_url}")
            try:
                client = TradingClient(
                    api_key, 
                    secret_key, 
                    api_version='v2',
                    raw_data=False,
                    url_override=base_url
                )
                account = client.get_account()
                print(f"   ✅ SUCCESS with base URL!")
                print(f"   - Account Status: {account.status}")
                print(f"   - Portfolio Value: ${float(account.portfolio_value):,.2f}")
            except Exception as e2:
                print(f"   ❌ Failed with base_url: {e2}")

# Configuration 2: Using ALPACA_PAPER_API_KEY/SECRET
paper_api_key = os.getenv('ALPACA_PAPER_API_KEY')
paper_secret_key = os.getenv('ALPACA_PAPER_API_SECRET')
paper_base_url = os.getenv('ALPACA_PAPER_BASE_URL')

if paper_api_key and paper_secret_key:
    print("\n2️⃣ Testing with ALPACA_PAPER_API_KEY/SECRET:")
    try:
        client = TradingClient(paper_api_key, paper_secret_key, paper=True)
        account = client.get_account()
        print(f"   ✅ SUCCESS! Connected with PAPER variables")
        print(f"   - Account Status: {account.status}")
        print(f"   - Portfolio Value: ${float(account.portfolio_value):,.2f}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

# Test raw API call
print("\n3️⃣ Testing Raw API Call:")
import requests

if api_key and secret_key:
    headers = {
        'APCA-API-KEY-ID': api_key,
        'APCA-API-SECRET-KEY': secret_key
    }
    
    # Test paper trading endpoint
    url = 'https://paper-api.alpaca.markets/v2/account'
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Raw API call successful!")
            print(f"   - Status: {data.get('status')}")
            print(f"   - Buying Power: ${float(data.get('buying_power', 0)):,.2f}")
        else:
            print(f"   ❌ API returned status code: {response.status_code}")
            print(f"   - Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Raw API call failed: {e}")

# Recommendations
print("\n💡 Recommendations:")
print("-" * 30)

if not (api_key and secret_key):
    print("❗ Set these environment variables in DigitalOcean:")
    print("   ALPACA_API_KEY=your_key_here")
    print("   ALPACA_SECRET_KEY=your_secret_here")
else:
    print("✅ Environment variables are set")
    print("\n📝 In your app.py, make sure you're using:")
    print("   api_key = os.getenv('ALPACA_API_KEY')")
    print("   secret_key = os.getenv('ALPACA_SECRET_KEY')")
    print("   trading_client = TradingClient(api_key, secret_key, paper=True)")

print("\n🔗 Your Alpaca Dashboard:")
print("   https://app.alpaca.markets/paper/dashboard/overview")
print("   Check if your API keys are active there")

print("\n" + "=" * 50)
print("Test complete!")
