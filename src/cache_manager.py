"""
Cache manager for Strava API responses to improve performance
"""
import json
import os
import pickle
from datetime import datetime, timedelta
from typing import Any, Optional
import hashlib


class CacheManager:
    def __init__(self, cache_dir: str = "cache", cache_duration_hours: int = 24):
        self.cache_dir = cache_dir
        self.cache_duration = timedelta(hours=cache_duration_hours)
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Generate cache file path from key"""
        # Create a safe filename from the cache key
        safe_key = hashlib.md5(cache_key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{safe_key}.cache")
    
    def _is_cache_valid(self, cache_path: str) -> bool:
        """Check if cache file exists and is still valid"""
        if not os.path.exists(cache_path):
            return False
        
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        return datetime.now() - file_time < self.cache_duration
    
    def get(self, cache_key: str) -> Optional[Any]:
        """Get cached data if available and valid"""
        cache_path = self._get_cache_path(cache_key)
        
        if self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Warning: Error reading cache file {cache_path}: {e}")
                # Remove corrupted cache file
                try:
                    os.remove(cache_path)
                except:
                    pass
        
        return None
    
    def set(self, cache_key: str, data: Any) -> None:
        """Store data in cache"""
        cache_path = self._get_cache_path(cache_key)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"Warning: Error writing to cache file {cache_path}: {e}")
    
    def clear(self) -> None:
        """Clear all cached data"""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    os.remove(os.path.join(self.cache_dir, filename))
        except Exception as e:
            print(f"Warning: Error clearing cache: {e}")
    
    def get_activities_cache_key(self, days_back: int, access_token: str) -> str:
        """Generate cache key for activities data"""
        # Include a hash of the access token for security
        token_hash = hashlib.md5(access_token.encode()).hexdigest()[:8]
        return f"activities_{days_back}_{token_hash}"
    
    def get_streams_cache_key(self, activity_id: int, access_token: str) -> str:
        """Generate cache key for activity streams data"""
        token_hash = hashlib.md5(access_token.encode()).hexdigest()[:8]
        return f"streams_{activity_id}_{token_hash}"
