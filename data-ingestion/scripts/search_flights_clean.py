#!/usr/bin/env python3
"""
VoYatra Flight Search - User Interface
Easy way to search flights without remembering Scrapy commands
"""

import os
import subprocess
import sys
from datetime import datetime, timedelta

def get_user_input():
    """Get flight search parameters from user"""
    print("✈️  Welcome to VoYatra Flight Search!")
    print("=" * 50)
    
    # Get origin
    origin = input("🛫 From (city name or airport code): ").strip()
    if not origin:
        origin = "delhi"
        print(f"   Using default: {origin}")
    
    # Get destination  
    destination = input("🛬 To (city name or airport code): ").strip()
    if not destination:
        destination = "mumbai"
        print(f"   Using default: {destination}")
    
    # Get departure date
    departure_date = input("📅 Departure date (YYYY-MM-DD or DD/MM/YYYY) [press Enter for tomorrow]: ").strip()
    if not departure_date:
        tomorrow = datetime.now() + timedelta(days=1)
        departure_date = tomorrow.strftime('%Y-%m-%d')
        print(f"   Using default: {departure_date}")
    
    # Get return date (optional)
    return_date = input("🔄 Return date (optional, same format): ").strip()
    if not return_date:
        return_date = None
        print("   One-way flight selected")
    
    return origin, destination, departure_date, return_date

def build_scrapy_command(origin, destination, departure_date, return_date=None):
    """Build Scrapy command with user parameters"""
    cmd = [
        sys.executable, '-m', 'scrapy', 'crawl', 'flights_spider',
        '-a', f'origin={origin}',
        '-a', f'destination={destination}',
        '-a', f'departure_date={departure_date}'
    ]
    
    if return_date:
        cmd.extend(['-a', f'return_date={return_date}'])
    
    return cmd

def run_flight_search():
    """Main function to run flight search"""
    try:
        # Get user input
        origin, destination, departure_date, return_date = get_user_input()
        
        # Build command
        cmd = build_scrapy_command(origin, destination, departure_date, return_date)
        
        print("\n🚀 Starting flight search...")
        print("=" * 50)
        print("🔍 Searching on: Expedia, Kayak, Skyscanner, MakeMyTrip, Goibibo")
        
        if return_date:
            print(f"✈️  Route: {origin.upper()} → {destination.upper()} → {origin.upper()}")
            print(f"📅 Dates: {departure_date} to {return_date}")
        else:
            print(f"✈️  Route: {origin.upper()} → {destination.upper()}")
            print(f"📅 Date: {departure_date}")
        
        print("\n⏳ This may take 2-5 minutes depending on website response times...")
        print("📊 Results will be saved to data/raw/flights/")
        print("=" * 50)
        
        # Change to scrapers directory
        scrapers_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scrapers')
        print(f"\n🔧 Working directory: {os.path.abspath(scrapers_dir)}")
        
        # Run the scraper
        result = subprocess.run(cmd, cwd=scrapers_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("\n✅ Flight search completed successfully!")
            print("📄 Check the data/raw/flights/ directory for results")
            if result.stdout:
                print("\n📝 Output:")
                print(result.stdout[-500:])  # Show last 500 characters
        else:
            print("\n❌ Flight search encountered some issues")
            print("💡 Error details:")
            if result.stderr:
                print(result.stderr[-500:])  # Show last 500 characters
            if result.stdout:
                print("📝 Output:")
                print(result.stdout[-500:])
        
    except KeyboardInterrupt:
        print("\n🛑 Search cancelled by user")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you're in the data-ingestion directory")
        print("2. Ensure all requirements are installed: pip install -r requirements.txt")
        print("3. Try running directly: cd scrapers && python -m scrapy crawl flights_spider")

if __name__ == "__main__":
    run_flight_search()
