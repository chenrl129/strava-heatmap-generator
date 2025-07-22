"""
Configuration and utility functions for the Strava Heatmap Generator
"""
import os
from typing import Dict, Any


class Config:
    """Configuration settings for the application"""
    
    # Strava API settings
    STRAVA_BASE_URL = "https://www.strava.com/api/v3"
    STRAVA_RATE_LIMIT = 600  # requests per 15 minutes
    
    # Map settings
    DEFAULT_MAP_CENTER = [40.7128, -74.0060]  # NYC
    DEFAULT_ZOOM = 12
    MAX_ACTIVITIES_PER_REQUEST = 200
    
    # File settings
    OUTPUT_DIR = "maps"
    SUPPORTED_ACTIVITY_TYPES = ["Ride", "VirtualRide"]
    
    # Color schemes for different map types
    HEATMAP_GRADIENT = {0.4: 'blue', 0.65: 'lime', 1: 'red'}
    
    SPEED_COLORS = {
        'very_slow': {'color': 'blue', 'threshold': 15},
        'slow': {'color': 'green', 'threshold': 25},
        'moderate': {'color': 'orange', 'threshold': 35},
        'fast': {'color': 'red', 'threshold': float('inf')}
    }
    
    # Route colors for individual route visualization
    ROUTE_COLORS = [
        'red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred',
        'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white',
        'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray'
    ]
    
    @classmethod
    def from_env(cls) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        return {
            'STRAVA_CLIENT_ID': os.getenv('STRAVA_CLIENT_ID'),
            'STRAVA_CLIENT_SECRET': os.getenv('STRAVA_CLIENT_SECRET'),
            'STRAVA_ACCESS_TOKEN': os.getenv('STRAVA_ACCESS_TOKEN'),
            'FLASK_SECRET_KEY': os.getenv('FLASK_SECRET_KEY', 'dev-key'),
            'FLASK_DEBUG': os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
            'DEFAULT_MAP_CENTER_LAT': float(os.getenv('DEFAULT_MAP_CENTER_LAT', '40.7128')),
            'DEFAULT_MAP_CENTER_LON': float(os.getenv('DEFAULT_MAP_CENTER_LON', '-74.0060')),
            'DEFAULT_ZOOM': int(os.getenv('DEFAULT_ZOOM', '12'))
        }


def validate_credentials(client_id: str, client_secret: str, access_token: str) -> bool:
    """Validate that all required Strava credentials are provided"""
    return all([
        client_id and client_id.strip(),
        client_secret and client_secret.strip(),
        access_token and access_token.strip()
    ])


def format_distance(distance_meters: float) -> str:
    """Format distance from meters to human-readable string"""
    if distance_meters < 1000:
        return f"{distance_meters:.0f} m"
    else:
        return f"{distance_meters / 1000:.2f} km"


def format_duration(seconds: int) -> str:
    """Format duration from seconds to human-readable string"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def format_speed(speed_ms: float) -> str:
    """Format speed from m/s to km/h"""
    speed_kmh = speed_ms * 3.6
    return f"{speed_kmh:.1f} km/h"


def get_speed_color(speed_kmh: float) -> str:
    """Get color based on speed for visualization"""
    for category, config in Config.SPEED_COLORS.items():
        if speed_kmh < config['threshold']:
            return config['color']
    return Config.SPEED_COLORS['fast']['color']


def create_map_legend_html(legend_type: str) -> str:
    """Create HTML legend for different map types"""
    legends = {
        'speed': '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 150px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px; border-radius: 10px;">
        <p><b>Speed Legend</b></p>
        <p><i class="fa fa-circle" style="color:blue"></i> &lt; 15 km/h</p>
        <p><i class="fa fa-circle" style="color:green"></i> 15-25 km/h</p>
        <p><i class="fa fa-circle" style="color:orange"></i> 25-35 km/h</p>
        <p><i class="fa fa-circle" style="color:red"></i> &gt; 35 km/h</p>
        </div>
        ''',
        
        'elevation': '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 180px; height: 100px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px; border-radius: 10px;">
        <p><b>Elevation Legend</b></p>
        <p>Low to High Elevation</p>
        <div style="height: 20px; background: linear-gradient(to right, #8B4513, #228B22, #FFFF00, #FFFFFF); border-radius: 5px;"></div>
        </div>
        '''
    }
    
    return legends.get(legend_type, '')


def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if division by zero"""
    try:
        return a / b if b != 0 else default
    except (TypeError, ZeroDivisionError):
        return default


def clean_coordinates(coordinates: list) -> list:
    """Clean and validate GPS coordinates"""
    cleaned = []
    for coord in coordinates:
        if (isinstance(coord, (list, tuple)) and 
            len(coord) >= 2 and
            isinstance(coord[0], (int, float)) and
            isinstance(coord[1], (int, float)) and
            -90 <= coord[0] <= 90 and  # Valid latitude
            -180 <= coord[1] <= 180):  # Valid longitude
            cleaned.append([float(coord[0]), float(coord[1])])
    return cleaned
