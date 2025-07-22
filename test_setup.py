#!/usr/bin/env python3
"""
Test script to verify Strava Heatmap Generator setup
"""
import os
import sys
from dotenv import load_dotenv

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from strava_api import StravaAPI
from config import Config, validate_credentials


def test_strava_connection():
    """Test connection to Strava API"""
    print("🧪 Testing Strava Heatmap Generator Setup")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    config = Config.from_env()
    
    # Check credentials
    client_id = config['STRAVA_CLIENT_ID']
    client_secret = config['STRAVA_CLIENT_SECRET']
    access_token = config['STRAVA_ACCESS_TOKEN']
    
    print("📋 Checking credentials...")
    if not validate_credentials(client_id, client_secret, access_token):
        print("❌ Missing or invalid Strava API credentials!")
        print("   Please check your .env file contains:")
        print("   - STRAVA_CLIENT_ID")
        print("   - STRAVA_CLIENT_SECRET")
        print("   - STRAVA_ACCESS_TOKEN")
        return False
    
    print("✅ Credentials found")
    
    # Test API connection
    print("🔌 Testing Strava API connection...")
    try:
        strava_api = StravaAPI(client_id, client_secret, access_token)
        athlete_info = strava_api.get_athlete_info()
        
        print(f"✅ Connected successfully!")
        print(f"   Athlete: {athlete_info.get('firstname', '')} {athlete_info.get('lastname', '')}")
        print(f"   Location: {athlete_info.get('city', 'Unknown')}, {athlete_info.get('country', 'Unknown')}")
        print(f"   Followers: {athlete_info.get('follower_count', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Strava API: {e}")
        return False


def test_dependencies():
    """Test that all required dependencies are available"""
    print("\\n📦 Testing dependencies...")
    
    required_packages = [
        'requests', 'pandas', 'folium', 'matplotlib', 
        'plotly', 'flask', 'dotenv', 'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'dotenv':
                import dotenv
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies available")
    return True


def main():
    """Main test function"""
    print("🚀 Strava Heatmap Generator - Setup Test\\n")
    
    # Test dependencies first
    deps_ok = test_dependencies()
    
    # Test Strava connection
    strava_ok = test_strava_connection()
    
    print("\\n" + "=" * 50)
    
    if deps_ok and strava_ok:
        print("🎉 Setup test passed! You're ready to generate heatmaps!")
        print("\\n🌐 To start the web interface:")
        print("   python app.py")
        print("\\n💻 To use the command line:")
        print("   python generate_heatmaps.py --help")
        return True
    else:
        print("❌ Setup test failed. Please fix the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
