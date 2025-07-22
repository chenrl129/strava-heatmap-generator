#!/usr/bin/env python3
"""
OAuth helper script to get a properly scoped Strava access token
"""
import requests
import webbrowser
from urllib.parse import parse_qs, urlparse
import sys


def get_strava_token(client_id, client_secret):
    """Get a new Strava access token with proper scopes"""
    
    # Step 1: Open authorization URL
    auth_url = (
        f"https://www.strava.com/oauth/authorize?"
        f"client_id={client_id}&"
        f"response_type=code&"
        f"redirect_uri=http://localhost&"
        f"approval_prompt=force&"
        f"scope=activity:read_all"
    )
    
    print("🚀 Strava OAuth Helper")
    print("=" * 30)
    print("\\n1. Opening Strava authorization page in your browser...")
    print("2. Please authorize the application")
    print("3. You'll be redirected to a localhost page (which may show an error - that's OK!)")
    print("4. Copy the full URL from your browser's address bar\\n")
    
    try:
        webbrowser.open(auth_url)
    except:
        print("⚠️  Could not open browser automatically.")
        print(f"Please manually open this URL: {auth_url}")
    
    # Step 2: Get authorization code from user
    print("\\nWaiting for authorization...")
    redirect_url = input("\\nPaste the full redirect URL here: ").strip()
    
    if not redirect_url:
        print("❌ No URL provided")
        return None
    
    # Extract code from URL
    try:
        parsed_url = urlparse(redirect_url)
        query_params = parse_qs(parsed_url.query)
        
        if 'code' not in query_params:
            print("❌ No authorization code found in URL")
            print("Make sure you copied the complete URL after authorization")
            return None
        
        code = query_params['code'][0]
        print(f"✅ Found authorization code: {code[:10]}...")
        
    except Exception as e:
        print(f"❌ Error parsing URL: {e}")
        return None
    
    # Step 3: Exchange code for token
    print("\\n🔄 Exchanging code for access token...")
    
    token_url = "https://www.strava.com/oauth/token"
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'grant_type': 'authorization_code'
    }
    
    try:
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            
            print("✅ Success! Token obtained")
            print(f"   Athlete: {token_data.get('athlete', {}).get('firstname', 'Unknown')}")
            print(f"   Scope: {token_data.get('scope', 'Unknown')}")
            
            return token_data
        else:
            print(f"❌ Failed to get token: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error requesting token: {e}")
        return None


def update_env_file(access_token, client_id, client_secret):
    """Update the .env file with new credentials"""
    env_content = f"""# Strava API credentials
STRAVA_CLIENT_ID={client_id}
STRAVA_CLIENT_SECRET={client_secret}
STRAVA_ACCESS_TOKEN={access_token}

# Flask configuration
FLASK_SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True

# Map settings
DEFAULT_MAP_CENTER_LAT=40.7128
DEFAULT_MAP_CENTER_LON=-74.0060
DEFAULT_ZOOM=10
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Updated .env file with new credentials")


def main():
    """Main function"""
    print("🔐 Strava Access Token Generator")
    print("This will help you get a properly scoped access token\\n")
    
    # Get credentials
    client_id = input("Enter your Strava Client ID: ").strip()
    if not client_id:
        print("❌ Client ID is required")
        sys.exit(1)
    
    client_secret = input("Enter your Strava Client Secret: ").strip()
    if not client_secret:
        print("❌ Client Secret is required")
        sys.exit(1)
    
    # Get token
    token_data = get_strava_token(client_id, client_secret)
    
    if not token_data:
        print("\\n❌ Failed to get access token")
        print("\\nTroubleshooting tips:")
        print("1. Make sure your Client ID and Secret are correct")
        print("2. Ensure you authorized the application")
        print("3. Copy the complete redirect URL")
        sys.exit(1)
    
    access_token = token_data['access_token']
    
    print("\\n" + "=" * 50)
    print("🎉 SUCCESS!")
    print("=" * 50)
    print(f"\\nYour new access token: {access_token}")
    print(f"Expires in: {token_data.get('expires_in', 'Unknown')} seconds")
    print(f"Scopes: {token_data.get('scope', 'Unknown')}")
    
    # Offer to update .env file
    update_env = input("\\nUpdate .env file with these credentials? (y/n): ").lower().strip()
    if update_env in ['y', 'yes']:
        update_env_file(access_token, client_id, client_secret)
    else:
        print("\\n📝 Manually add this to your .env file:")
        print(f"STRAVA_ACCESS_TOKEN={access_token}")
    
    print("\\n🧪 Next steps:")
    print("1. Run: python test_setup.py")
    print("2. If successful, run: python generate_heatmaps.py --help")
    print("3. Or start the web app: python app.py")


if __name__ == "__main__":
    main()
