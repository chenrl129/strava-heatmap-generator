#!/usr/bin/env python3
"""
Simple test to verify Strava API connection
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from strava_api import StravaAPI
    
    def test_strava_connection():
        """Test connection to Strava API"""
        print("🧪 Testing Strava API Connection")
        print("=" * 40)
        
        # Get credentials from environment
        client_id = os.getenv('STRAVA_CLIENT_ID')
        client_secret = os.getenv('STRAVA_CLIENT_SECRET')
        access_token = os.getenv('STRAVA_ACCESS_TOKEN')
        
        if not all([client_id, client_secret, access_token]):
            print("❌ Missing Strava credentials in .env file")
            return False
        
        print(f"✅ Client ID: {client_id}")
        print(f"✅ Client Secret: {'*' * 20}")
        print(f"✅ Access Token: {'*' * 20}")
        
        try:
            # Initialize API client
            api = StravaAPI(client_id, client_secret, access_token)
            
            # Test getting athlete info
            print("\n🔄 Testing athlete information...")
            athlete = api.get_athlete_info()
            print(f"✅ Connected as: {athlete.get('firstname', 'Unknown')} {athlete.get('lastname', '')}")
            
            # Test getting recent activities
            print("\n🔄 Testing activity retrieval...")
            activities = api.get_activities(limit=5)
            print(f"✅ Found {len(activities)} recent activities")
            
            if activities:
                activity = activities[0]
                print(f"   Latest: {activity.get('name', 'Unnamed')} ({activity.get('distance', 0)/1000:.1f} km)")
            
            print("\n🎉 All tests passed! Your Strava setup is working correctly.")
            return True
            
        except Exception as e:
            print(f"❌ Error testing Strava API: {e}")
            return False
    
    if __name__ == "__main__":
        success = test_strava_connection()
        sys.exit(0 if success else 1)
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)
