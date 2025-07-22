#!/usr/bin/env python3
"""
Command-line interface for Strava Heatmap Generator
"""
import os
import sys
import argparse
from dotenv import load_dotenv

from src.strava_api import StravaAPI
from src.heatmap_generator import StravaHeatmapGenerator


def main():
    """Main function for CLI"""
    parser = argparse.ArgumentParser(description='Generate Strava Activity Heatmaps')
    parser.add_argument('--days', type=int, default=365, help='Number of days back to fetch activities (default: 365)')
    parser.add_argument('--limit', type=int, default=50, help='Maximum number of activities to process for detailed maps (default: 50)')
    parser.add_argument('--maps', nargs='+', default=['basic', 'speed', 'elevation', 'routes'], 
                       choices=['basic', 'speed', 'elevation', 'routes', 'stats'],
                       help='Types of maps to generate (default: all)')
    parser.add_argument('--output-dir', default='maps', help='Output directory for generated maps (default: maps)')
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Get Strava API credentials
    client_id = os.getenv('STRAVA_CLIENT_ID')
    client_secret = os.getenv('STRAVA_CLIENT_SECRET')
    access_token = os.getenv('STRAVA_ACCESS_TOKEN')
    
    if not all([client_id, client_secret, access_token]):
        print("Error: Missing Strava API credentials!")
        print("Please set STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, and STRAVA_ACCESS_TOKEN in your .env file")
        sys.exit(1)
    
    try:
        # Initialize Strava API
        print("Initializing Strava API...")
        strava_api = StravaAPI(client_id, client_secret, access_token)
        
        # Get athlete info
        athlete_info = strava_api.get_athlete_info()
        print(f"Connected to Strava account: {athlete_info.get('firstname', '')} {athlete_info.get('lastname', '')}")
        
        # Get activities summary
        print(f"\\nFetching activities from the last {args.days} days...")
        activities_df = strava_api.get_all_cycling_activities(days_back=args.days)
        
        if activities_df.empty:
            print("No cycling activities found in the specified time period.")
            return
        
        print(f"Found {len(activities_df)} cycling activities")
        print(f"Total distance: {activities_df['distance_km'].sum():.2f} km")
        print(f"Total time: {activities_df['moving_time_hours'].sum():.2f} hours")
        
        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Initialize heatmap generator
        heatmap_generator = StravaHeatmapGenerator()
        
        # Generate statistics chart if requested
        if 'stats' in args.maps:
            print("\\nGenerating activity statistics chart...")
            stats_file = os.path.join(args.output_dir, 'activity_stats.png')
            heatmap_generator.create_activity_stats_chart(activities_df, stats_file)
        
        # Get detailed GPS data for maps
        map_types = [m for m in args.maps if m != 'stats']
        if map_types:
            print(f"\\nFetching detailed GPS data for up to {args.limit} activities...")
            activity_ids = activities_df['id'].head(args.limit).tolist()
            detailed_activities = strava_api.get_activities_with_detailed_streams(activity_ids=activity_ids)
            
            if not detailed_activities:
                print("No activities with GPS data found.")
                return
            
            print(f"Successfully loaded GPS data for {len(detailed_activities)} activities")
            
            # Generate maps
            for map_type in map_types:
                print(f"\\nGenerating {map_type} map...")
                output_file = os.path.join(args.output_dir, f'{map_type}_heatmap.html')
                
                if map_type == 'basic':
                    heatmap_generator.create_basic_heatmap(detailed_activities, output_file)
                elif map_type == 'speed':
                    heatmap_generator.create_speed_heatmap(detailed_activities, output_file)
                elif map_type == 'elevation':
                    heatmap_generator.create_elevation_heatmap(detailed_activities, output_file)
                elif map_type == 'routes':
                    heatmap_generator.create_route_map(detailed_activities, output_file)
        
        print(f"\\n✅ All maps generated successfully!")
        print(f"📁 Output directory: {os.path.abspath(args.output_dir)}")
        print(f"🌐 Open the HTML files in your web browser to view the maps")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
