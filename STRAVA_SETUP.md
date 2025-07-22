# Strava API Setup Guide

## 🔐 Getting Your Strava API Credentials

### Step 1: Create a Strava Application

1. Go to [Strava API Settings](https://www.strava.com/settings/api)
2. Click "Create App" or "My API Application"
3. Fill in the application details:
   - **Application Name**: "My Heatmap Generator"
   - **Category**: "Data Importer"
   - **Club**: Leave blank
   - **Website**: Your website or `http://localhost:5000`
   - **Authorization Callback Domain**: `localhost`
   - **Description**: "Personal heatmap generator for cycling activities"

4. After creation, note down:
   - **Client ID** (public)
   - **Client Secret** (keep private!)

### Step 2: Get Access Token with Proper Scopes

The access token in your API Info.txt might not have the right permissions. You need `activity:read` scope.

#### Option A: Use Strava's OAuth Playground

1. Go to: `https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=activity:read_all`

2. Replace `YOUR_CLIENT_ID` with your actual Client ID

3. You'll be redirected to a URL like: `http://localhost/?state=&code=AUTHORIZATION_CODE&scope=read,activity:read_all`

4. Copy the `AUTHORIZATION_CODE` from the URL

5. Exchange the code for an access token:
   ```bash
   curl -X POST https://www.strava.com/oauth/token \
     -F client_id=YOUR_CLIENT_ID \
     -F client_secret=YOUR_CLIENT_SECRET \
     -F code=AUTHORIZATION_CODE \
     -F grant_type=authorization_code
   ```

#### Option B: Use Our Helper Script

```python
# oauth_helper.py
import requests
import webbrowser
from urllib.parse import parse_qs, urlparse

def get_strava_token(client_id, client_secret):
    # Step 1: Open authorization URL
    auth_url = f"https://www.strava.com/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=activity:read_all"
    
    print("Opening Strava authorization page...")
    webbrowser.open(auth_url)
    
    # Step 2: Get authorization code from user
    redirect_url = input("After authorizing, copy the full URL you were redirected to: ")
    
    # Extract code from URL
    parsed_url = urlparse(redirect_url)
    code = parse_qs(parsed_url.query)['code'][0]
    
    # Step 3: Exchange code for token
    token_url = "https://www.strava.com/oauth/token"
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'grant_type': 'authorization_code'
    }
    
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data['access_token']
    else:
        raise Exception(f"Failed to get token: {response.text}")

if __name__ == "__main__":
    client_id = input("Enter your Strava Client ID: ")
    client_secret = input("Enter your Strava Client Secret: ")
    
    try:
        access_token = get_strava_token(client_id, client_secret)
        print(f"\\nSuccess! Your access token is: {access_token}")
        print("\\nAdd this to your .env file:")
        print(f"STRAVA_ACCESS_TOKEN={access_token}")
    except Exception as e:
        print(f"Error: {e}")
```

### Step 3: Update Your .env File

```env
STRAVA_CLIENT_ID=169258
STRAVA_CLIENT_SECRET=339bddecb5c26318a197aecb67871792ac59348f
STRAVA_ACCESS_TOKEN=YOUR_NEW_ACCESS_TOKEN_WITH_ACTIVITY_READ_SCOPE

# Flask configuration
FLASK_SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True

# Map settings
DEFAULT_MAP_CENTER_LAT=40.7128
DEFAULT_MAP_CENTER_LON=-74.0060
DEFAULT_ZOOM=10
```

## 🔍 Troubleshooting

### "Authorization Error" / "missing activity:read_permission"

This means your access token doesn't have permission to read activities. You need to:

1. Get a new access token with `activity:read_all` scope (see Step 2 above)
2. Update your `.env` file with the new token
3. Run the test again: `python test_setup.py`

### "Invalid access token"

Your token might have expired. Strava tokens are valid for 6 hours. You need to either:

1. Get a new access token (quick fix)
2. Implement refresh token flow (advanced)

### "No activities found"

- Check your activities are not private
- Try increasing the `--days` parameter
- Ensure you have cycling activities in the time range

## 🔒 Security Notes

- **Never share your Client Secret or Access Token**
- **Don't commit credentials to git repositories**
- **Use environment variables (.env file)**
- **The .env file is in .gitignore for your protection**

## 📋 Required Scopes

For this application to work, you need:

- `activity:read_all` - Read all activities (public and private)

Optional scopes for enhanced features:
- `profile:read_all` - Read detailed profile information
- `activity:read` - Read only public activities (if you prefer less access)

## 🛠 Manual Token Generation (Advanced)

If the helper script doesn't work, you can manually go through the OAuth flow:

1. **Authorization URL**: 
   ```
   https://www.strava.com/oauth/authorize?client_id=169258&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=activity:read_all
   ```

2. **Get the code from redirect URL**

3. **Exchange for token**:
   ```bash
   curl -X POST https://www.strava.com/oauth/token \
     -F client_id=169258 \
     -F client_secret=339bddecb5c26318a197aecb67871792ac59348f \
     -F code=YOUR_AUTHORIZATION_CODE \
     -F grant_type=authorization_code
   ```

The response will contain your `access_token` that you can use in the `.env` file.

---

Once you have the correct access token with `activity:read_all` scope, run:

```bash
python test_setup.py
```

If successful, you can then generate your heatmaps! 🎉
