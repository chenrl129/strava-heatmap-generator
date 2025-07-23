"""
Advanced heatmap and visualization methods for the StravaHeatmapGenerator
"""
import folium
from folium.plugins import HeatMap, HeatMapWithTime, MarkerCluster, MiniMap, Draw
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import json
from collections import defaultdict


class AdvancedVisualizationMixin:
    """Mixin class containing advanced visualization methods"""
    
    def create_time_animated_heatmap(self, activities_data: List[Dict], output_file: str, time_period: str = 'month') -> None:
        """Create animated heatmap showing activity over time"""
        print("Creating time-animated heatmap...")
        
        if not activities_data:
            print("No activity data available for time animation")
            return
        
        # Group activities by time period
        time_groups = defaultdict(list)
        
        for activity in activities_data:
            coords = activity.get('coordinates', [])
            activity_id = activity.get('id')
            
            # For now, we'll group by activity (since we don't have timestamps in the data)
            # In a real implementation, you'd group by actual time periods
            if coords:
                time_groups[f"Activity {activity_id}"].extend([[coord[0], coord[1], 1] for coord in coords])
        
        if not time_groups:
            print("No coordinate data found for time animation")
            return
        
        # Create map
        center = self._calculate_activity_density_center(activities_data)
        zoom = self._calculate_optimal_zoom(activities_data)
        
        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles='OpenStreetMap'
        )
        
        # Prepare data for HeatMapWithTime
        heat_data = []
        time_index = []
        
        for time_period, coords in time_groups.items():
            if coords:
                # Sample coordinates for performance
                sampled_coords = self._sample_coordinates(coords, max_points=500)
                heat_data.append(sampled_coords)
                time_index.append(time_period)
        
        if heat_data:
            # Add animated heatmap
            HeatMapWithTime(
                heat_data,
                index=time_index,
                auto_play=True,
                max_opacity=0.8,
                radius=15,
                blur=10,
                speed_step=0.5
            ).add_to(m)
        
        # Add minimap
        minimap = MiniMap(toggle_display=True)
        m.add_child(minimap)
        
        # Save map
        m.save(output_file)
        print(f"Time-animated heatmap saved to: {output_file}")
    
    def create_clustered_activity_map(self, activities_data: List[Dict], output_file: str) -> None:
        """Create a map with clustered activity start/end points"""
        print("Creating clustered activity map...")
        
        if not activities_data:
            print("No activity data available for clustering")
            return
        
        center = self._calculate_activity_density_center(activities_data)
        zoom = self._calculate_optimal_zoom(activities_data)
        
        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles='OpenStreetMap'
        )
        
        # Create marker clusters for start and end points
        start_cluster = MarkerCluster(name="Activity Start Points").add_to(m)
        end_cluster = MarkerCluster(name="Activity End Points").add_to(m)
        
        for activity in activities_data:
            coords = activity.get('coordinates', [])
            activity_id = activity.get('id', 'Unknown')
            
            if len(coords) >= 2:
                # Start point
                start_coord = coords[0]
                folium.Marker(
                    location=[start_coord[0], start_coord[1]],
                    popup=f"Activity {activity_id} - Start",
                    icon=folium.Icon(color='green', icon='play')
                ).add_to(start_cluster)
                
                # End point
                end_coord = coords[-1]
                folium.Marker(
                    location=[end_coord[0], end_coord[1]],
                    popup=f"Activity {activity_id} - End",
                    icon=folium.Icon(color='red', icon='stop')
                ).add_to(end_cluster)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add minimap
        minimap = MiniMap(toggle_display=True)
        m.add_child(minimap)
        
        # Save map
        m.save(output_file)
        print(f"Clustered activity map saved to: {output_file}")
    
    def create_interactive_route_explorer(self, activities_data: List[Dict], output_file: str) -> None:
        """Create an interactive map where users can draw and explore routes"""
        print("Creating interactive route explorer...")
        
        if not activities_data:
            print("No activity data available for route explorer")
            return
        
        center = self._calculate_activity_density_center(activities_data)
        zoom = self._calculate_optimal_zoom(activities_data)
        
        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles='OpenStreetMap'
        )
        
        # Add different tile layers
        folium.TileLayer('Stamen Terrain', name='Terrain').add_to(m)
        folium.TileLayer('Stamen Toner', name='Toner').add_to(m)
        folium.TileLayer('CartoDB positron', name='Light').add_to(m)
        
        # Add all routes as separate layers
        route_colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 
                       'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 
                       'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 
                       'gray', 'black', 'lightgray']
        
        for i, activity in enumerate(activities_data[:20]):  # Limit to first 20 for performance
            coords = activity.get('coordinates', [])
            activity_id = activity.get('id', f'Activity_{i}')
            
            if len(coords) >= 2:
                # Sample coordinates for performance
                sampled_coords = self._sample_coordinates(coords, max_points=200)
                
                # Calculate route statistics
                stats = self._calculate_route_statistics(activity)
                
                # Create popup with route information
                popup_text = f"""
                <b>Activity {activity_id}</b><br>
                Distance: {stats['distance_km']:.2f} km<br>
                Avg Speed: {stats['avg_speed_kmh']:.1f} km/h<br>
                Max Speed: {stats['max_speed_kmh']:.1f} km/h<br>
                Max Elevation: {stats['max_elevation_m']:.0f} m<br>
                Elevation Gain: {stats['elevation_gain_m']:.0f} m
                """
                
                # Add route as polyline
                folium.PolyLine(
                    locations=sampled_coords,
                    color=route_colors[i % len(route_colors)],
                    weight=3,
                    opacity=0.8,
                    popup=folium.Popup(popup_text, max_width=300)
                ).add_to(m)
        
        # Add drawing tools
        draw = Draw(
            export=True,
            filename='drawn_route.geojson',
            position='topleft',
            draw_options={
                'polyline': True,
                'polygon': True,
                'circle': False,
                'rectangle': True,
                'marker': True,
                'circlemarker': False,
            },
            edit_options={'edit': True}
        )
        m.add_child(draw)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Save map
        m.save(output_file)
        print(f"Interactive route explorer saved to: {output_file}")
    
    def create_comparison_heatmap(self, activities_data: List[Dict], output_file: str, 
                                 comparison_metric: str = 'speed') -> None:
        """Create a heatmap comparing different metrics across routes"""
        print(f"Creating comparison heatmap for {comparison_metric}...")
        
        if not activities_data:
            print("No activity data available for comparison")
            return
        
        center = self._calculate_activity_density_center(activities_data)
        zoom = self._calculate_optimal_zoom(activities_data)
        
        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles='OpenStreetMap'
        )
        
        # Collect all data points with comparison values
        comparison_data = []
        
        for activity in activities_data:
            coords = activity.get('coordinates', [])
            
            if comparison_metric == 'speed':
                values = activity.get('velocity', [])
                # Convert m/s to km/h
                values = [v * 3.6 if v else 0 for v in values]
            elif comparison_metric == 'elevation':
                values = activity.get('altitude', [])
                values = [v if v is not None else 0 for v in values]
            else:
                values = [1] * len(coords)  # Default weight
            
            # Create weighted points
            for i, coord in enumerate(coords):
                if i < len(values) and len(coord) == 2:
                    weight = values[i] if values else 1
                    comparison_data.append([coord[0], coord[1], weight])
        
        if comparison_data:
            # Normalize weights for better visualization
            weights = [point[2] for point in comparison_data]
            if weights:
                max_weight = max(weights)
                min_weight = min(weights)
                weight_range = max_weight - min_weight if max_weight != min_weight else 1
                
                for point in comparison_data:
                    point[2] = ((point[2] - min_weight) / weight_range) * 2 + 0.5  # Scale to 0.5-2.5
            
            # Sample data for performance
            if len(comparison_data) > 2000:
                step = len(comparison_data) // 2000
                comparison_data = comparison_data[::step]
            
            # Add heatmap
            HeatMap(
                comparison_data,
                min_opacity=0.3,
                max_opacity=0.8,
                radius=15,
                blur=15,
                gradient={
                    0.2: 'blue',
                    0.4: 'cyan', 
                    0.6: 'lime',
                    0.8: 'yellow',
                    1.0: 'red'
                }
            ).add_to(m)
        
        # Add colorbar legend
        legend_html = f"""
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 150px; height: 90px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>{comparison_metric.title()} Heatmap</b></p>
        <p><i class="fa fa-circle" style="color:blue"></i> Low</p>
        <p><i class="fa fa-circle" style="color:yellow"></i> Medium</p>
        <p><i class="fa fa-circle" style="color:red"></i> High</p>
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Save map
        m.save(output_file)
        print(f"Comparison heatmap ({comparison_metric}) saved to: {output_file}")
