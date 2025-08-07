#!/usr/bin/env python3
"""
Flight Search Demo with Anti-Bot Bypass
This script demonstrates different approaches to scraping flight data
"""

import subprocess
import sys
import time
from datetime import datetime, timedelta

class FlightSearchDemo:
    def __init__(self):
        self.scrapers_path = r"d:\VoYatra\data-ingestion\scrapers"
        
    def run_basic_spider(self):
        """Run basic spider (may face blocks)"""
        print("🚀 Running Basic Spider...")
        cmd = [
            'python', '-m', 'scrapy', 'crawl', 'flights_spider',
            '-a', 'origin=delhi',
            '-a', 'destination=mumbai', 
            '-a', 'departure_date=2025-08-12'
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.scrapers_path, capture_output=True, text=True, timeout=60)
            print("✅ Basic spider completed")
            return result
        except subprocess.TimeoutExpired:
            print("⏰ Basic spider timed out (expected due to blocks)")
            return None
    
    def run_enhanced_spider(self):
        """Run enhanced spider with anti-detection"""
        print("🛡️ Running Enhanced Spider with Anti-Detection...")
        cmd = [
            'python', '-m', 'scrapy', 'crawl', 'flights_spider_enhanced',
            '-a', 'origin=delhi',
            '-a', 'destination=mumbai',
            '-a', 'departure_date=2025-08-12',
            '-s', 'DOWNLOAD_DELAY=5',
            '-s', 'RANDOMIZE_DOWNLOAD_DELAY=0.8'
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.scrapers_path, capture_output=True, text=True, timeout=120)
            print("✅ Enhanced spider completed")
            return result
        except subprocess.TimeoutExpired:
            print("⏰ Enhanced spider timed out")
            return None
    
    def demonstrate_api_approach(self):
        """Demonstrate API-based approach"""
        print("📡 API Approach Demonstration...")
        print("""
        API-based scraping is the most reliable approach:
        
        1. Amadeus Travel API:
           - Sign up: https://developers.amadeus.com/
           - 2000 free requests/month
           - No anti-bot measures
           
        2. RapidAPI Flight APIs:
           - Multiple providers available
           - Paid but reliable
           - Structured data
           
        3. Airline Direct APIs:
           - Air India, SpiceJet, IndiGo
           - Often less protected
           - Best for specific airlines
        """)
    
    def show_success_strategies(self):
        """Show successful strategies for different scenarios"""
        print("""
        🎯 Success Strategies by Use Case:
        
        📊 For Price Monitoring:
        ✅ Use APIs (Amadeus, RapidAPI)
        ✅ Focus on airline direct websites  
        ✅ Implement email alert parsing
        
        🔍 For Comprehensive Data:
        ✅ Combine multiple APIs
        ✅ Use mobile user agents
        ✅ Implement proxy rotation
        
        ⚡ For Quick Results:
        ✅ Start with Amadeus API
        ✅ Use historical data sources
        ✅ Focus on less protected endpoints
        
        🛡️ For Anti-Detection:
        ✅ Random delays (3-7 seconds)
        ✅ Rotate user agents
        ✅ Use residential proxies
        ✅ Implement session management
        """)

def main():
    demo = FlightSearchDemo()
    
    print("=" * 60)
    print("🛩️  FLIGHT DATA SCRAPING ANTI-BOT BYPASS DEMO")
    print("=" * 60)
    
    print("\n1️⃣ Showing why basic scraping fails...")
    basic_result = demo.run_basic_spider()
    time.sleep(2)
    
    print("\n2️⃣ Demonstrating enhanced approach...")
    enhanced_result = demo.run_enhanced_spider()
    time.sleep(2)
    
    print("\n3️⃣ API-First Approach (Recommended)...")
    demo.demonstrate_api_approach()
    
    print("\n4️⃣ Success Strategies Summary...")
    demo.show_success_strategies()
    
    print("\n" + "=" * 60)
    print("📝 RECOMMENDATIONS:")
    print("=" * 60)
    print("""
    🥇 IMMEDIATE ACTION: Sign up for Amadeus API
       → https://developers.amadeus.com/
       → Get 2000 free requests/month
       → No bot blocks, reliable data
    
    🥈 PARALLEL DEVELOPMENT: Enhanced spider
       → Use flights_spider_enhanced.py
       → Add proxy rotation
       → Implement CAPTCHA solving
    
    🥉 LONG-TERM: Hybrid approach
       → Combine APIs + selective scraping
       → Focus on less protected sources
       → Monitor success rates
    """)

if __name__ == "__main__":
    main()
