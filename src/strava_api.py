"""
Strava API client for fetching activity data
"""
import os
import sys
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import time

# Add the parent directory to the path to import cache_manager
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from cache_manager import CacheManager


class StravaAPI:
    def __init__(self, client_id: str, client_secret: str, access_token: str, enable_cache: bool = True):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.base_url = "https://www.strava.com/api/v3"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Initialize cache manager if enabled
        self.cache_manager = CacheManager() if enable_cache else None
        
        # Rate limiting - Strava allows 100 requests per 15 minutes, 1000 per day
        self.request_count = 0
        self.last_request_time = 0
        self.rate_limit_delay = 0.6  # Minimum delay between requests
    
    def _make_request(self, url: str, params: Optional[Dict] = None, retries: int = 3) -> requests.Response:
        """Make a rate-limited request to Strava API with retry logic"""
        for attempt in range(retries):
            try:
                # Rate limiting
                current_time = time.time()
                time_since_last = current_time - self.last_request_time
                if time_since_last < self.rate_limit_delay:
                    time.sleep(self.rate_limit_delay - time_since_last)
                
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
                self.last_request_time = time.time()
                self.request_count += 1
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 900))  # Default 15 minutes
                    print(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                
                # Check for other errors
                if response.status_code >= 400:
                    print(f"API error {response.status_code}: {response.text}")
                    if attempt == retries - 1:  # Last attempt
                        response.raise_for_status()
                    continue
                
                return response
                
            except requests.exceptions.RequestException as e:
                print(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt == retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception(f"Failed to make request after {retries} attempts")
    
    def get_athlete_info(self) -> Dict:
        """Get authenticated athlete information"""
        url = f"{self.base_url}/athlete"
        response = self._make_request(url)
        return response.json()
    
    def get_activities(self, limit: int = 200, page: int = 1, after: Optional[datetime] = None) -> List[Dict]:
        """Get athlete activities"""
        url = f"{self.base_url}/athlete/activities"
        params = {
            "per_page": min(limit, 200),  # Strava API limit is 200 per page
            "page": page
        }
        
        if after:
            params["after"] = int(after.timestamp())
        
        response = self._make_request(url, params)
        return response.json()
    
    def get_activity_streams(self, activity_id: int, stream_types: List[str] = None) -> Dict:
        """Get activity streams (GPS coordinates, elevation, etc.) with caching"""
        if stream_types is None:
            stream_types = ["latlng", "altitude", "velocity_smooth", "distance", "time"]
        
        # Check cache first
        if self.cache_manager:
            cache_key = self.cache_manager.get_streams_cache_key(activity_id, self.access_token)
            cached_data = self.cache_manager.get(cache_key)
            if cached_data is not None:
                return cached_data
        
        stream_types_str = ",".join(stream_types)
        url = f"{self.base_url}/activities/{activity_id}/streams"
        params = {
            "keys": stream_types_str,
            "key_by_type": "true"
        }
        
        try:
            response = self._make_request(url, params)
            data = response.json()
            
            # Cache the result
            if self.cache_manager:
                self.cache_manager.set(cache_key, data)
            
            return data
            
        except Exception as e:
            print(f"Warning: Failed to get streams for activity {activity_id}: {e}")
            return {}
    
    def get_all_cycling_activities(self, days_back: int = 365) -> pd.DataFrame:
        """Get all cycling activities with GPS data, using cache when possible"""
        # Check cache first
        if self.cache_manager:
            cache_key = self.cache_manager.get_activities_cache_key(days_back, self.access_token)
            cached_data = self.cache_manager.get(cache_key)
            if cached_data is not None:
                print(f"Using cached activities data ({len(cached_data)} activities)")
                return pd.DataFrame(cached_data)
        
        after_date = datetime.now() - timedelta(days=days_back)
        all_activities = []
        page = 1
        
        print("Fetching activities from Strava...")
        
        while True:
            activities = self.get_activities(limit=200, page=page, after=after_date)
            
            if not activities:
                break
            
            # Filter for cycling activities with GPS data
            cycling_activities = [
                activity for activity in activities 
                if activity.get('type') in ['Ride', 'VirtualRide', 'EBikeRide'] and 
                   activity.get('map', {}).get('summary_polyline') and
                   activity.get('distance', 0) > 500  # Filter out very short activities (< 0.5km)
            ]
            
            all_activities.extend(cycling_activities)
            
            if len(activities) < 200:  # Last page
                break
            
            page += 1
            print(f"Fetched page {page-1}, found {len(cycling_activities)} cycling activities...")
        
        print(f"Found {len(all_activities)} cycling activities total")
        
        # Cache the raw data
        if self.cache_manager and all_activities:
            self.cache_manager.set(cache_key, all_activities)
        
        # Convert to DataFrame
        df = pd.DataFrame(all_activities)
        
        if not df.empty:
            df['start_date'] = pd.to_datetime(df['start_date'])
            df['distance_km'] = df['distance'] / 1000
            df['moving_time_hours'] = df['moving_time'] / 3600
            df['average_speed_kmh'] = df['average_speed'] * 3.6
            
            # Add additional useful columns
            df['elevation_gain_m'] = df.get('total_elevation_gain', 0)
            df['suffer_score'] = df.get('suffer_score', 0)
            df['achievement_count'] = df.get('achievement_count', 0)
        
        return df
    
    def get_activities_with_detailed_streams(self, activity_ids: List[int] = None, limit: int = 50) -> List[Dict]:
        """Get activities with detailed GPS streams for heatmap generation"""
        if activity_ids is None:
            # Get recent cycling activities
            activities_df = self.get_all_cycling_activities(days_back=365)
            if activities_df.empty:
                return []
            
            # Sort by date and take the most recent ones
            activities_df = activities_df.sort_values('start_date', ascending=False)
            activity_ids = activities_df['id'].head(limit).tolist()
        
        detailed_activities = []
        failed_activities = []
        
        print(f"Fetching detailed GPS data for {len(activity_ids)} activities...")
        
        for i, activity_id in enumerate(activity_ids):
            print(f"Processing activity {i+1}/{len(activity_ids)}: {activity_id}")
            
            try:
                streams = self.get_activity_streams(activity_id)
                
                if 'latlng' in streams and streams['latlng'].get('data'):
                    # Validate GPS coordinates
                    coords = streams['latlng']['data']
                    valid_coords = []
                    
                    for coord in coords:
                        if (len(coord) == 2 and 
                            -90 <= coord[0] <= 90 and  # Valid latitude
                            -180 <= coord[1] <= 180):  # Valid longitude
                            valid_coords.append(coord)
                    
                    if len(valid_coords) >= 10:  # Minimum points for meaningful visualization
                        activity_data = {
                            'id': activity_id,
                            'coordinates': valid_coords,
                            'altitude': streams.get('altitude', {}).get('data', []),
                            'velocity': streams.get('velocity_smooth', {}).get('data', []),
                            'distance': streams.get('distance', {}).get('data', []),
                            'time': streams.get('time', {}).get('data', [])
                        }
                        detailed_activities.append(activity_data)
                    else:
                        print(f"Activity {activity_id} has insufficient valid GPS points ({len(valid_coords)})")
                        failed_activities.append(activity_id)
                else:
                    print(f"Activity {activity_id} has no GPS data")
                    failed_activities.append(activity_id)
                
            except Exception as e:
                print(f"Error processing activity {activity_id}: {e}")
                failed_activities.append(activity_id)
                continue
        
        if failed_activities:
            print(f"Warning: Failed to process {len(failed_activities)} activities: {failed_activities[:5]}{'...' if len(failed_activities) > 5 else ''}")
        
        print(f"Successfully processed {len(detailed_activities)} activities with GPS data")
        return detailed_activities

    def clear_cache(self) -> None:
        """Clear the API cache"""
        if self.cache_manager:
            self.cache_manager.clear()
            print("Cache cleared successfully")
        else:
            print("Cache is not enabled")
