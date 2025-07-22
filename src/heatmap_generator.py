"""
Heatmap generator for Strava activity data
"""
import os
import folium
from folium.plugins import HeatMap, HeatMapWithTime
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from datetime import datetime
import json


class StravaHeatmapGenerator:
    def __init__(self):
        self.default_center = [40.7128, -74.0060]  # Default to NYC
        self.default_zoom = 12
    
    def _calculate_map_center(self, activities_data: List[Dict]) -> Tuple[float, float]:
        """Calculate the center point of all activities"""
        all_lats = []
        all_lons = []
        
        for activity in activities_data:
            coords = activity.get('coordinates', [])
            for coord in coords:
                if len(coord) == 2:
                    all_lats.append(coord[0])
                    all_lons.append(coord[1])
        
        if all_lats and all_lons:
            return [np.mean(all_lats), np.mean(all_lons)]
        else:
            return self.default_center
    
    def create_basic_heatmap(self, activities_data: List[Dict], output_file: str = "basic_heatmap.html") -> folium.Map:
        """Create a basic heatmap from all activity coordinates"""
        print("Creating basic heatmap...")
        
        # Calculate map center
        center = self._calculate_map_center(activities_data)
        
        # Create base map
        m = folium.Map(
            location=center,
            zoom_start=self.default_zoom,
            tiles='OpenStreetMap'
        )
        
        # Collect all coordinates
        heat_data = []
        for activity in activities_data:
            coords = activity.get('coordinates', [])
            for coord in coords:
                if len(coord) == 2:
                    heat_data.append([coord[0], coord[1]])
        
        if heat_data:
            # Add heatmap layer
            HeatMap(
                heat_data,
                radius=8,
                blur=10,
                gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}
            ).add_to(m)
            
            print(f"Added {len(heat_data)} GPS points to heatmap")
        else:
            print("No GPS data found for heatmap")
        
        # Save map
        m.save(output_file)
        print(f"Basic heatmap saved to {output_file}")
        
        return m
    
    def create_speed_heatmap(self, activities_data: List[Dict], output_file: str = "speed_heatmap.html") -> folium.Map:
        """Create a heatmap colored by speed"""
        print("Creating speed-based heatmap...")
        
        center = self._calculate_map_center(activities_data)
        m = folium.Map(location=center, zoom_start=self.default_zoom)
        
        # Collect coordinates with speed data
        for activity in activities_data:
            coords = activity.get('coordinates', [])
            velocities = activity.get('velocity', [])
            
            if coords and velocities and len(coords) == len(velocities):
                # Convert velocity to km/h and create color-coded points
                for i, (coord, velocity) in enumerate(zip(coords, velocities)):
                    if len(coord) == 2 and velocity > 0:
                        speed_kmh = velocity * 3.6  # Convert m/s to km/h
                        
                        # Color based on speed
                        if speed_kmh < 15:
                            color = 'blue'
                        elif speed_kmh < 25:
                            color = 'green'
                        elif speed_kmh < 35:
                            color = 'orange'
                        else:
                            color = 'red'
                        
                        # Add every 10th point to avoid overcrowding
                        if i % 10 == 0:
                            folium.CircleMarker(
                                location=[coord[0], coord[1]],
                                radius=2,
                                color=color,
                                fillColor=color,
                                fillOpacity=0.6,
                                popup=f"Speed: {speed_kmh:.1f} km/h"
                            ).add_to(m)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 150px; height: 90px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>Speed Legend</b></p>
        <p><i class="fa fa-circle" style="color:blue"></i> &lt; 15 km/h</p>
        <p><i class="fa fa-circle" style="color:green"></i> 15-25 km/h</p>
        <p><i class="fa fa-circle" style="color:orange"></i> 25-35 km/h</p>
        <p><i class="fa fa-circle" style="color:red"></i> &gt; 35 km/h</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        m.save(output_file)
        print(f"Speed heatmap saved to {output_file}")
        
        return m
    
    def create_elevation_heatmap(self, activities_data: List[Dict], output_file: str = "elevation_heatmap.html") -> folium.Map:
        """Create a heatmap colored by elevation"""
        print("Creating elevation-based heatmap...")
        
        center = self._calculate_map_center(activities_data)
        m = folium.Map(location=center, zoom_start=self.default_zoom)
        
        # Collect all elevations to determine color scale
        all_elevations = []
        for activity in activities_data:
            elevations = activity.get('altitude', [])
            all_elevations.extend([e for e in elevations if e is not None])
        
        if not all_elevations:
            print("No elevation data found")
            return m
        
        min_elevation = min(all_elevations)
        max_elevation = max(all_elevations)
        elevation_range = max_elevation - min_elevation
        
        # Create colormap
        colormap = cm.get_cmap('terrain')
        
        for activity in activities_data:
            coords = activity.get('coordinates', [])
            elevations = activity.get('altitude', [])
            
            if coords and elevations and len(coords) == len(elevations):
                for i, (coord, elevation) in enumerate(zip(coords, elevations)):
                    if len(coord) == 2 and elevation is not None:
                        # Normalize elevation for color mapping
                        if elevation_range > 0:
                            normalized_elevation = (elevation - min_elevation) / elevation_range
                        else:
                            normalized_elevation = 0.5
                        
                        # Get color from colormap
                        rgba = colormap(normalized_elevation)
                        color = f'#{int(rgba[0]*255):02x}{int(rgba[1]*255):02x}{int(rgba[2]*255):02x}'
                        
                        # Add every 15th point to avoid overcrowding
                        if i % 15 == 0:
                            folium.CircleMarker(
                                location=[coord[0], coord[1]],
                                radius=2,
                                color=color,
                                fillColor=color,
                                fillOpacity=0.7,
                                popup=f"Elevation: {elevation:.1f} m"
                            ).add_to(m)
        
        # Add elevation legend
        legend_html = f'''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 180px; height: 80px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>Elevation Legend</b></p>
        <p>Min: {min_elevation:.0f} m</p>
        <p>Max: {max_elevation:.0f} m</p>
        <div style="height: 20px; background: linear-gradient(to right, #8B4513, #228B22, #FFFF00, #FFFFFF);"></div>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        m.save(output_file)
        print(f"Elevation heatmap saved to {output_file}")
        
        return m
    
    def create_route_map(self, activities_data: List[Dict], output_file: str = "routes_map.html") -> folium.Map:
        """Create a map showing individual routes"""
        print("Creating routes map...")
        
        center = self._calculate_map_center(activities_data)
        m = folium.Map(location=center, zoom_start=self.default_zoom)
        
        # Color palette for different routes
        colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 
                 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 
                 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']
        
        for i, activity in enumerate(activities_data[:20]):  # Limit to 20 routes for visibility
            coords = activity.get('coordinates', [])
            
            if coords:
                # Convert coordinates for folium
                route_coords = [[coord[0], coord[1]] for coord in coords if len(coord) == 2]
                
                if route_coords:
                    color = colors[i % len(colors)]
                    
                    folium.PolyLine(
                        locations=route_coords,
                        color=color,
                        weight=3,
                        opacity=0.7,
                        popup=f"Route {i+1} (Activity ID: {activity.get('id', 'Unknown')})"
                    ).add_to(m)
        
        m.save(output_file)
        print(f"Routes map saved to {output_file}")
        
        return m
    
    def create_activity_stats_chart(self, activities_df: pd.DataFrame, output_file: str = "activity_stats.png"):
        """Create charts showing activity statistics"""
        if activities_df.empty:
            print("No activity data for charts")
            return
        
        print("Creating activity statistics chart...")
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Strava Activity Statistics', fontsize=16, fontweight='bold')
        
        # 1. Distance distribution
        ax1.hist(activities_df['distance_km'], bins=20, alpha=0.7, color='blue', edgecolor='black')
        ax1.set_xlabel('Distance (km)')
        ax1.set_ylabel('Number of Activities')
        ax1.set_title('Distance Distribution')
        ax1.grid(True, alpha=0.3)
        
        # 2. Speed distribution
        if 'average_speed_kmh' in activities_df.columns:
            ax2.hist(activities_df['average_speed_kmh'], bins=20, alpha=0.7, color='green', edgecolor='black')
            ax2.set_xlabel('Average Speed (km/h)')
            ax2.set_ylabel('Number of Activities')
            ax2.set_title('Speed Distribution')
            ax2.grid(True, alpha=0.3)
        
        # 3. Activities over time
        activities_df['month'] = activities_df['start_date'].dt.to_period('M')
        monthly_counts = activities_df.groupby('month').size()
        ax3.plot(monthly_counts.index.astype(str), monthly_counts.values, marker='o', color='red')
        ax3.set_xlabel('Month')
        ax3.set_ylabel('Number of Activities')
        ax3.set_title('Activities Over Time')
        ax3.tick_params(axis='x', rotation=45)
        ax3.grid(True, alpha=0.3)
        
        # 4. Total distance by month
        monthly_distance = activities_df.groupby('month')['distance_km'].sum()
        ax4.bar(range(len(monthly_distance)), monthly_distance.values, alpha=0.7, color='orange')
        ax4.set_xlabel('Month')
        ax4.set_ylabel('Total Distance (km)')
        ax4.set_title('Monthly Distance')
        ax4.set_xticks(range(len(monthly_distance)))
        ax4.set_xticklabels([str(x) for x in monthly_distance.index], rotation=45)
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Activity statistics chart saved to {output_file}")
        plt.close()
    
    def generate_all_maps(self, activities_data: List[Dict], activities_df: pd.DataFrame) -> Dict[str, str]:
        """Generate all types of maps and return file paths"""
        output_files = {}
        
        if activities_data:
            output_files['basic'] = "maps/basic_heatmap.html"
            output_files['speed'] = "maps/speed_heatmap.html"
            output_files['elevation'] = "maps/elevation_heatmap.html"
            output_files['routes'] = "maps/routes_map.html"
            
            # Create maps directory
            os.makedirs("maps", exist_ok=True)
            
            self.create_basic_heatmap(activities_data, output_files['basic'])
            self.create_speed_heatmap(activities_data, output_files['speed'])
            self.create_elevation_heatmap(activities_data, output_files['elevation'])
            self.create_route_map(activities_data, output_files['routes'])
        
        if not activities_df.empty:
            output_files['stats'] = "maps/activity_stats.png"
            self.create_activity_stats_chart(activities_df, output_files['stats'])
        
        return output_files
