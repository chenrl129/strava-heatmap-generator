"""
Strava API client for fetching activity data
"""
import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json


class StravaAPI:
    def __init__(self, client_id: str, client_secret: str, access_token: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.base_url = "https://www.strava.com/api/v3"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def get_athlete_info(self) -> Dict:
        """Get authenticated athlete information"""
        url = f"{self.base_url}/athlete"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get athlete info: {response.status_code} - {response.text}")
    
    def get_activities(self, limit: int = 200, page: int = 1, after: Optional[datetime] = None) -> List[Dict]:
        """Get athlete activities"""
        url = f"{self.base_url}/athlete/activities"
        params = {
            "per_page": min(limit, 200),  # Strava API limit is 200 per page
            "page": page
        }
        
        if after:
            params["after"] = int(after.timestamp())
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get activities: {response.status_code} - {response.text}")
    
    def get_activity_streams(self, activity_id: int, stream_types: List[str] = None) -> Dict:
        """Get activity streams (GPS coordinates, elevation, etc.)"""
        if stream_types is None:
            stream_types = ["latlng", "altitude", "velocity_smooth", "distance", "time"]
        
        stream_types_str = ",".join(stream_types)
        url = f"{self.base_url}/activities/{activity_id}/streams"
        params = {
            "keys": stream_types_str,
            "key_by_type": "true"
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Warning: Failed to get streams for activity {activity_id}: {response.status_code}")
            return {}
    
    def get_all_cycling_activities(self, days_back: int = 365) -> pd.DataFrame:
        """Get all cycling activities with GPS data"""
        after_date = datetime.now() - timedelta(days=days_back)
        all_activities = []
        page = 1
        
        print("Fetching activities from Strava...")
        
        while True:
            activities = self.get_activities(limit=200, page=page, after=after_date)
            
            if not activities:
                break
            
            # Filter for cycling activities
            cycling_activities = [
                activity for activity in activities 
                if activity.get('type') in ['Ride', 'VirtualRide'] and activity.get('map', {}).get('summary_polyline')
            ]
            
            all_activities.extend(cycling_activities)
            
            if len(activities) < 200:  # Last page
                break
            
            page += 1
        
        print(f"Found {len(all_activities)} cycling activities")
        
        # Convert to DataFrame
        df = pd.DataFrame(all_activities)
        
        if not df.empty:
            df['start_date'] = pd.to_datetime(df['start_date'])
            df['distance_km'] = df['distance'] / 1000
            df['moving_time_hours'] = df['moving_time'] / 3600
            df['average_speed_kmh'] = df['average_speed'] * 3.6
        
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
        
        print(f"Fetching detailed GPS data for {len(activity_ids)} activities...")
        
        for i, activity_id in enumerate(activity_ids):
            print(f"Processing activity {i+1}/{len(activity_ids)}: {activity_id}")
            
            try:
                streams = self.get_activity_streams(activity_id)
                
                if 'latlng' in streams and streams['latlng'].get('data'):
                    activity_data = {
                        'id': activity_id,
                        'coordinates': streams['latlng']['data'],
                        'altitude': streams.get('altitude', {}).get('data', []),
                        'velocity': streams.get('velocity_smooth', {}).get('data', []),
                        'distance': streams.get('distance', {}).get('data', []),
                        'time': streams.get('time', {}).get('data', [])
                    }
                    detailed_activities.append(activity_data)
                
            except Exception as e:
                print(f"Error processing activity {activity_id}: {e}")
                continue
        
        print(f"Successfully processed {len(detailed_activities)} activities with GPS data")
        return detailed_activities
