"""
Enhanced statistics and analytics for Strava activities
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json


class StravaAnalytics:
    """Advanced analytics for Strava cycling data"""
    
    def __init__(self):
        self.style_config = {
            'figure.figsize': (12, 8),
            'axes.titlesize': 16,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10
        }
        plt.rcParams.update(self.style_config)
    
    def analyze_activity_patterns(self, activities_df: pd.DataFrame) -> Dict:
        """Comprehensive analysis of activity patterns"""
        if activities_df.empty:
            return {'error': 'No activity data available'}
        
        analysis = {}
        
        # Basic statistics
        analysis['basic_stats'] = {
            'total_activities': len(activities_df),
            'total_distance_km': activities_df['distance_km'].sum(),
            'total_time_hours': activities_df['moving_time_hours'].sum(),
            'avg_distance_km': activities_df['distance_km'].mean(),
            'avg_speed_kmh': activities_df['average_speed_kmh'].mean(),
            'max_distance_km': activities_df['distance_km'].max(),
            'max_speed_kmh': activities_df['average_speed_kmh'].max()
        }
        
        # Time-based patterns
        activities_df['hour'] = activities_df['start_date'].dt.hour
        activities_df['day_of_week'] = activities_df['start_date'].dt.day_name()
        activities_df['month'] = activities_df['start_date'].dt.month_name()
        
        analysis['time_patterns'] = {
            'most_active_hour': activities_df['hour'].value_counts().idxmax(),
            'most_active_day': activities_df['day_of_week'].value_counts().idxmax(),
            'most_active_month': activities_df['month'].value_counts().idxmax(),
            'hourly_distribution': activities_df['hour'].value_counts().to_dict(),
            'daily_distribution': activities_df['day_of_week'].value_counts().to_dict(),
            'monthly_distribution': activities_df['month'].value_counts().to_dict()
        }
        
        # Performance trends
        activities_df['date'] = activities_df['start_date'].dt.date
        daily_stats = activities_df.groupby('date').agg({
            'distance_km': 'sum',
            'moving_time_hours': 'sum',
            'average_speed_kmh': 'mean'
        }).reset_index()
        
        # Calculate moving averages
        window = min(7, len(daily_stats))  # 7-day moving average or less if insufficient data
        if window > 1:
            daily_stats['distance_ma'] = daily_stats['distance_km'].rolling(window=window, center=True).mean()
            daily_stats['speed_ma'] = daily_stats['average_speed_kmh'].rolling(window=window, center=True).mean()
        
        analysis['performance_trends'] = {
            'improvement_trend': self._calculate_trend(daily_stats['average_speed_kmh']),
            'consistency_score': self._calculate_consistency(activities_df),
            'peak_performance_period': self._find_peak_period(daily_stats)
        }
        
        # Activity categorization
        analysis['activity_categories'] = self._categorize_activities(activities_df)
        
        return analysis
    
    def _calculate_trend(self, series: pd.Series) -> str:
        """Calculate if there's an improving, declining, or stable trend"""
        if len(series) < 3:
            return "Insufficient data"
        
        # Simple linear regression slope
        x = np.arange(len(series))
        slope = np.polyfit(x, series.dropna(), 1)[0]
        
        if slope > 0.1:
            return "Improving"
        elif slope < -0.1:
            return "Declining"
        else:
            return "Stable"
    
    def _calculate_consistency(self, activities_df: pd.DataFrame) -> float:
        """Calculate consistency score based on regular activity patterns"""
        if len(activities_df) < 7:
            return 0.0
        
        # Group by week and count activities
        activities_df['week'] = activities_df['start_date'].dt.isocalendar().week
        activities_df['year'] = activities_df['start_date'].dt.year
        weekly_counts = activities_df.groupby(['year', 'week']).size()
        
        # Calculate coefficient of variation (lower = more consistent)
        if len(weekly_counts) > 1 and weekly_counts.std() > 0:
            cv = weekly_counts.std() / weekly_counts.mean()
            consistency_score = max(0, 1 - cv / 2)  # Scale to 0-1
        else:
            consistency_score = 1.0 if len(weekly_counts) == 1 else 0.0
        
        return round(consistency_score * 100, 1)  # Return as percentage
    
    def _find_peak_period(self, daily_stats: pd.DataFrame) -> Dict:
        """Find the period with best performance"""
        if len(daily_stats) < 7:
            return {'period': 'Insufficient data', 'avg_speed': 0}
        
        # Calculate 7-day rolling average of speed
        daily_stats['speed_7d'] = daily_stats['average_speed_kmh'].rolling(window=7, center=True).mean()
        
        if daily_stats['speed_7d'].isna().all():
            return {'period': 'No data available', 'avg_speed': 0}
        
        peak_idx = daily_stats['speed_7d'].idxmax()
        peak_date = daily_stats.loc[peak_idx, 'date']
        peak_speed = daily_stats.loc[peak_idx, 'speed_7d']
        
        return {
            'period': peak_date.strftime('%B %Y'),
            'avg_speed': round(peak_speed, 2)
        }
    
    def _categorize_activities(self, activities_df: pd.DataFrame) -> Dict:
        """Categorize activities by distance and intensity"""
        categories = {
            'short_rides': 0,      # < 20 km
            'medium_rides': 0,     # 20-50 km  
            'long_rides': 0,       # 50-100 km
            'epic_rides': 0,       # > 100 km
            'leisurely': 0,        # < 15 km/h
            'moderate': 0,         # 15-25 km/h
            'fast': 0,             # 25-35 km/h
            'racing': 0            # > 35 km/h
        }
        
        # Distance categories
        categories['short_rides'] = len(activities_df[activities_df['distance_km'] < 20])
        categories['medium_rides'] = len(activities_df[(activities_df['distance_km'] >= 20) & (activities_df['distance_km'] < 50)])
        categories['long_rides'] = len(activities_df[(activities_df['distance_km'] >= 50) & (activities_df['distance_km'] < 100)])
        categories['epic_rides'] = len(activities_df[activities_df['distance_km'] >= 100])
        
        # Speed categories
        categories['leisurely'] = len(activities_df[activities_df['average_speed_kmh'] < 15])
        categories['moderate'] = len(activities_df[(activities_df['average_speed_kmh'] >= 15) & (activities_df['average_speed_kmh'] < 25)])
        categories['fast'] = len(activities_df[(activities_df['average_speed_kmh'] >= 25) & (activities_df['average_speed_kmh'] < 35)])
        categories['racing'] = len(activities_df[activities_df['average_speed_kmh'] >= 35])
        
        return categories
    
    def create_comprehensive_dashboard(self, activities_df: pd.DataFrame, output_file: str) -> None:
        """Create a comprehensive analytics dashboard"""
        if activities_df.empty:
            print("No activity data available for dashboard creation")
            return
        
        # Set up the figure with subplots
        fig = plt.figure(figsize=(20, 16))
        gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)
        
        # 1. Distance over time
        ax1 = fig.add_subplot(gs[0, :2])
        activities_df.set_index('start_date')['distance_km'].resample('W').sum().plot(ax=ax1, color='#2E86AB')
        ax1.set_title('Weekly Distance Progression', fontweight='bold')
        ax1.set_ylabel('Distance (km)')
        ax1.grid(True, alpha=0.3)
        
        # 2. Speed distribution
        ax2 = fig.add_subplot(gs[0, 2:])
        activities_df['average_speed_kmh'].hist(bins=20, ax=ax2, color='#A23B72', alpha=0.7, edgecolor='black')
        ax2.set_title('Speed Distribution', fontweight='bold')
        ax2.set_xlabel('Average Speed (km/h)')
        ax2.set_ylabel('Frequency')
        ax2.grid(True, alpha=0.3)
        
        # 3. Activity patterns by hour
        ax3 = fig.add_subplot(gs[1, :2])
        hourly_counts = activities_df['start_date'].dt.hour.value_counts().sort_index()
        hourly_counts.plot(kind='bar', ax=ax3, color='#F18F01')
        ax3.set_title('Activities by Hour of Day', fontweight='bold')
        ax3.set_xlabel('Hour')
        ax3.set_ylabel('Number of Activities')
        ax3.tick_params(axis='x', rotation=0)
        
        # 4. Activity patterns by day of week
        ax4 = fig.add_subplot(gs[1, 2:])
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_counts = activities_df['start_date'].dt.day_name().value_counts().reindex(day_order)
        daily_counts.plot(kind='bar', ax=ax4, color='#C73E1D')
        ax4.set_title('Activities by Day of Week', fontweight='bold')
        ax4.set_xlabel('Day')
        ax4.set_ylabel('Number of Activities')
        ax4.tick_params(axis='x', rotation=45)
        
        # 5. Distance vs Speed scatter
        ax5 = fig.add_subplot(gs[2, :2])
        ax5.scatter(activities_df['distance_km'], activities_df['average_speed_kmh'], 
                   c=activities_df.index, cmap='viridis', alpha=0.6)
        ax5.set_title('Distance vs Average Speed', fontweight='bold')
        ax5.set_xlabel('Distance (km)')
        ax5.set_ylabel('Average Speed (km/h)')
        ax5.grid(True, alpha=0.3)
        
        # 6. Monthly activity summary
        ax6 = fig.add_subplot(gs[2, 2:])
        monthly_summary = activities_df.groupby(activities_df['start_date'].dt.to_period('M')).agg({
            'distance_km': 'sum',
            'moving_time_hours': 'sum'
        })
        monthly_summary['distance_km'].plot(kind='bar', ax=ax6, color='#6A994E')
        ax6.set_title('Monthly Distance Summary', fontweight='bold')
        ax6.set_xlabel('Month')
        ax6.set_ylabel('Total Distance (km)')
        ax6.tick_params(axis='x', rotation=45)
        
        # 7. Performance metrics over time
        ax7 = fig.add_subplot(gs[3, :])
        activities_df['cumulative_distance'] = activities_df['distance_km'].cumsum()
        activities_df['activity_number'] = range(1, len(activities_df) + 1)
        
        ax7_twin = ax7.twinx()
        line1 = ax7.plot(activities_df['activity_number'], activities_df['cumulative_distance'], 
                        'b-', linewidth=2, label='Cumulative Distance')
        line2 = ax7_twin.plot(activities_df['activity_number'], activities_df['average_speed_kmh'], 
                             'r-', linewidth=2, label='Average Speed', alpha=0.7)
        
        ax7.set_title('Performance Overview', fontweight='bold')
        ax7.set_xlabel('Activity Number')
        ax7.set_ylabel('Cumulative Distance (km)', color='blue')
        ax7_twin.set_ylabel('Average Speed (km/h)', color='red')
        
        # Combine legends
        lines1, labels1 = ax7.get_legend_handles_labels()
        lines2, labels2 = ax7_twin.get_legend_handles_labels()
        ax7.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        ax7.grid(True, alpha=0.3)
        
        # Add overall statistics text
        stats_text = f"""
        CYCLING STATISTICS SUMMARY
        
        Total Activities: {len(activities_df)}
        Total Distance: {activities_df['distance_km'].sum():.0f} km
        Total Time: {activities_df['moving_time_hours'].sum():.0f} hours
        Average Speed: {activities_df['average_speed_kmh'].mean():.1f} km/h
        Longest Ride: {activities_df['distance_km'].max():.1f} km
        Fastest Ride: {activities_df['average_speed_kmh'].max():.1f} km/h
        """
        
        fig.text(0.02, 0.98, stats_text, fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        plt.suptitle('Strava Cycling Analytics Dashboard', fontsize=24, fontweight='bold', y=0.98)
        
        # Save the dashboard
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"Analytics dashboard saved to: {output_file}")
    
    def generate_activity_report(self, activities_df: pd.DataFrame) -> Dict:
        """Generate a comprehensive activity report"""
        analysis = self.analyze_activity_patterns(activities_df)
        
        if 'error' in analysis:
            return analysis
        
        # Create insights based on analysis
        insights = []
        basic_stats = analysis['basic_stats']
        time_patterns = analysis['time_patterns']
        performance = analysis['performance_trends']
        categories = analysis['activity_categories']
        
        # Basic insights
        insights.append(f"You've completed {basic_stats['total_activities']} cycling activities")
        insights.append(f"Total distance covered: {basic_stats['total_distance_km']:.0f} km")
        insights.append(f"You prefer cycling on {time_patterns['most_active_day']}s")
        insights.append(f"Your most active time is {time_patterns['most_active_hour']}:00")
        
        # Performance insights
        if performance['improvement_trend'] == 'Improving':
            insights.append("🎉 Your performance is improving over time!")
        elif performance['improvement_trend'] == 'Declining':
            insights.append("📉 Your recent performance shows room for improvement")
        else:
            insights.append("📊 Your performance has been stable")
        
        insights.append(f"Consistency score: {performance['consistency_score']}%")
        
        # Activity type insights
        most_common_distance = max(categories, key=lambda x: categories[x] if 'rides' in x else 0)
        most_common_speed = max(categories, key=lambda x: categories[x] if x in ['leisurely', 'moderate', 'fast', 'racing'] else 0)
        
        insights.append(f"You mostly do {most_common_distance.replace('_', ' ')}")
        insights.append(f"Your typical pace is {most_common_speed}")
        
        return {
            'insights': insights,
            'detailed_analysis': analysis,
            'summary': f"Analysis based on {basic_stats['total_activities']} activities over {basic_stats['total_distance_km']:.0f} km"
        }
