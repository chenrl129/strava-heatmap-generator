"""
Flask web application for Strava Heatmap Generator
"""
import os
from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv
import json
from datetime import datetime

from src.strava_api import StravaAPI
from src.heatmap_generator import StravaHeatmapGenerator
from src.analytics import StravaAnalytics

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')

# Initialize global variables
strava_api = None
heatmap_generator = StravaHeatmapGenerator()
analytics = StravaAnalytics()


def initialize_strava_api():
    """Initialize Strava API client"""
    global strava_api
    
    client_id = os.getenv('STRAVA_CLIENT_ID')
    client_secret = os.getenv('STRAVA_CLIENT_SECRET')
    access_token = os.getenv('STRAVA_ACCESS_TOKEN')
    
    if not all([client_id, client_secret, access_token]):
        raise ValueError("Missing Strava API credentials in environment variables")
    
    strava_api = StravaAPI(client_id, client_secret, access_token)
    return strava_api


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/athlete')
def get_athlete():
    """Get athlete information"""
    try:
        if not strava_api:
            initialize_strava_api()
        
        athlete_info = strava_api.get_athlete_info()
        return jsonify({
            'success': True,
            'data': {
                'name': f"{athlete_info.get('firstname', '')} {athlete_info.get('lastname', '')}",
                'city': athlete_info.get('city', 'Unknown'),
                'state': athlete_info.get('state', 'Unknown'),
                'country': athlete_info.get('country', 'Unknown'),
                'profile_pic': athlete_info.get('profile_medium', ''),
                'follower_count': athlete_info.get('follower_count', 0),
                'friend_count': athlete_info.get('friend_count', 0)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/activities')
def get_activities():
    """Get activities summary"""
    try:
        if not strava_api:
            initialize_strava_api()
        
        days_back = request.args.get('days', 365, type=int)
        activities_df = strava_api.get_all_cycling_activities(days_back=days_back)
        
        if activities_df.empty:
            return jsonify({
                'success': True,
                'data': {
                    'total_activities': 0,
                    'total_distance': 0,
                    'total_time': 0,
                    'average_speed': 0
                }
            })
        
        total_distance = activities_df['distance_km'].sum()
        total_time = activities_df['moving_time_hours'].sum()
        avg_speed = activities_df['average_speed_kmh'].mean() if 'average_speed_kmh' in activities_df.columns else 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_activities': len(activities_df),
                'total_distance': round(total_distance, 2),
                'total_time': round(total_time, 2),
                'average_speed': round(avg_speed, 2),
                'date_range': {
                    'start': activities_df['start_date'].min().isoformat() if not activities_df.empty else None,
                    'end': activities_df['start_date'].max().isoformat() if not activities_df.empty else None
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/generate-heatmaps', methods=['POST'])
def generate_heatmaps():
    """Generate all heatmaps"""
    try:
        if not strava_api:
            initialize_strava_api()
        
        data = request.json
        map_types = data.get('map_types', ['basic', 'speed', 'elevation', 'routes'])
        activity_limit = data.get('activity_limit', 50)
        days_back = data.get('days_back', 365)
        
        # Get activities summary
        activities_df = strava_api.get_all_cycling_activities(days_back=days_back)
        
        # Get detailed GPS data
        if not activities_df.empty:
            activity_ids = activities_df['id'].head(activity_limit).tolist()
            detailed_activities = strava_api.get_activities_with_detailed_streams(
                activity_ids=activity_ids
            )
        else:
            detailed_activities = []
        
        # Create output directory
        os.makedirs('maps', exist_ok=True)
        
        generated_files = {}
        
        # Generate requested maps
        if 'basic' in map_types and detailed_activities:
            heatmap_generator.create_basic_heatmap(detailed_activities, 'maps/basic_heatmap.html')
            generated_files['basic'] = 'basic_heatmap.html'
        
        if 'speed' in map_types and detailed_activities:
            heatmap_generator.create_speed_heatmap(detailed_activities, 'maps/speed_heatmap.html')
            generated_files['speed'] = 'speed_heatmap.html'
        
        if 'elevation' in map_types and detailed_activities:
            heatmap_generator.create_elevation_heatmap(detailed_activities, 'maps/elevation_heatmap.html')
            generated_files['elevation'] = 'elevation_heatmap.html'
        
        if 'routes' in map_types and detailed_activities:
            heatmap_generator.create_route_map(detailed_activities, 'maps/routes_map.html')
            generated_files['routes'] = 'routes_map.html'
        
        # New advanced visualizations
        if 'animated' in map_types and detailed_activities:
            heatmap_generator.create_time_animated_heatmap(detailed_activities, 'maps/animated_heatmap.html')
            generated_files['animated'] = 'animated_heatmap.html'
        
        if 'clustered' in map_types and detailed_activities:
            heatmap_generator.create_clustered_activity_map(detailed_activities, 'maps/clustered_map.html')
            generated_files['clustered'] = 'clustered_map.html'
        
        if 'explorer' in map_types and detailed_activities:
            heatmap_generator.create_interactive_route_explorer(detailed_activities, 'maps/route_explorer.html')
            generated_files['explorer'] = 'route_explorer.html'
        
        if 'comparison' in map_types and detailed_activities:
            heatmap_generator.create_comparison_heatmap(detailed_activities, 'maps/comparison_heatmap.html', 'speed')
            generated_files['comparison'] = 'comparison_heatmap.html'
        
        # Generate statistics chart and dashboard
        if not activities_df.empty:
            heatmap_generator.create_activity_stats_chart(activities_df, 'maps/activity_stats.png')
            generated_files['stats'] = 'activity_stats.png'
            
            # Generate comprehensive analytics dashboard
            analytics.create_comprehensive_dashboard(activities_df, 'maps/analytics_dashboard.png')
            generated_files['dashboard'] = 'analytics_dashboard.png'
        
        return jsonify({
            'success': True,
            'data': {
                'generated_files': generated_files,
                'activities_processed': len(detailed_activities),
                'total_activities': len(activities_df) if not activities_df.empty else 0
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/clear-cache', methods=['POST'])
def clear_cache():
    """Clear API cache"""
    try:
        if strava_api:
            strava_api.clear_cache()
            return jsonify({'success': True, 'message': 'Cache cleared successfully'})
        else:
            return jsonify({'success': False, 'error': 'Strava API not initialized'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/activity-insights')
def get_activity_insights():
    """Get insights and statistics about activities"""
    try:
        if not strava_api:
            initialize_strava_api()
        
        days_back = request.args.get('days', 365, type=int)
        activities_df = strava_api.get_all_cycling_activities(days_back=days_back)
        
        if activities_df.empty:
            return jsonify({
                'success': True,
                'data': {'insights': [], 'summary': 'No activities found'}
            })
        
        # Use the enhanced analytics module
        report = analytics.generate_activity_report(activities_df)
        
        return jsonify({
            'success': True,
            'data': {
                'insights': report.get('insights', []),
                'summary': report.get('summary', ''),
                'detailed_analysis': report.get('detailed_analysis', {})
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/maps/<filename>')
def serve_map(filename):
    """Serve generated map files"""
    try:
        file_path = os.path.join('maps', filename)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return "File not found", 404
    except Exception as e:
        return str(e), 500


@app.route('/api/map-status')
def map_status():
    """Check which maps are available"""
    maps_dir = 'maps'
    available_maps = {}
    
    if os.path.exists(maps_dir):
        map_files = {
            'basic': 'basic_heatmap.html',
            'speed': 'speed_heatmap.html', 
            'elevation': 'elevation_heatmap.html',
            'routes': 'routes_map.html',
            'stats': 'activity_stats.png'
        }
        
        for map_type, filename in map_files.items():
            file_path = os.path.join(maps_dir, filename)
            available_maps[map_type] = {
                'available': os.path.exists(file_path),
                'filename': filename,
                'last_modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat() 
                              if os.path.exists(file_path) else None
            }
    
    return jsonify({'success': True, 'data': available_maps})


if __name__ == '__main__':
    try:
        initialize_strava_api()
        print("Strava API initialized successfully!")
        print("Starting Flask application...")
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Failed to initialize application: {e}")
        print("Please check your Strava API credentials in the .env file")
