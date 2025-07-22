# Strava Heatmap Generator - Usage Examples

## Quick Start Guide

### 1. Test Your Setup
```bash
python test_setup.py
```

### 2. Generate Basic Heatmap (CLI)
```bash
# Generate all map types for the last 6 months
python generate_heatmaps.py --days 180 --limit 50

# Generate only a speed heatmap
python generate_heatmaps.py --maps speed --days 90
```

### 3. Start Web Interface
```bash
python app.py
```
Then open `http://localhost:5000` in your browser.

## CLI Examples

### Basic Usage
```bash
# Default: last year, 50 activities, all map types
python generate_heatmaps.py

# Last 30 days, 25 activities
python generate_heatmaps.py --days 30 --limit 25

# Custom output directory
python generate_heatmaps.py --output-dir my_custom_maps
```

### Map Type Selection
```bash
# Only basic heatmap
python generate_heatmaps.py --maps basic

# Speed and elevation maps
python generate_heatmaps.py --maps speed elevation

# All except statistics
python generate_heatmaps.py --maps basic speed elevation routes
```

### Advanced Examples
```bash
# Process lots of activities (may take longer)
python generate_heatmaps.py --days 730 --limit 200

# Quick preview with recent activities
python generate_heatmaps.py --days 7 --limit 10 --maps basic
```

## Web Interface Features

### 1. Athlete Dashboard
- View your Strava profile information
- See total statistics (distance, time, activities)
- Real-time data updates

### 2. Configuration Options
- **Time Range**: 30 days to 2 years
- **Activity Limit**: 25 to 200 activities
- **Map Types**: Select any combination

### 3. Interactive Maps
- **Basic Heatmap**: Red hotspots show where you ride most
- **Speed Map**: Blue=slow, Green=medium, Orange=fast, Red=very fast
- **Elevation Map**: Color gradient from low to high elevation
- **Routes Map**: Individual colored lines for each ride

## Map Outputs

All maps are saved as HTML files that you can:
- Open in any web browser
- Share with friends
- Embed in websites
- Print or export as images

### File Locations
```
maps/
├── basic_heatmap.html      # General activity density
├── speed_heatmap.html      # Speed-colored points
├── elevation_heatmap.html  # Elevation-colored points
├── routes_map.html         # Individual route lines
└── activity_stats.png     # Statistics chart
```

## Tips for Best Results

### 1. Activity Selection
- **More activities = Better heatmaps** but slower processing
- **Recent activities** tend to have better GPS quality
- **Longer rides** provide more interesting elevation data

### 2. Performance
- Start with 25-50 activities to test
- Increase limit gradually for more detail
- Web interface shows progress for large datasets

### 3. Map Quality
- Ensure GPS is enabled during rides
- Activities need GPS tracks (not just summary data)
- Indoor/trainer rides won't appear on maps

### 4. Troubleshooting
- Check `.env` file has correct Strava credentials
- Verify activities are public or you have access
- Try reducing time range if no activities found

## API Rate Limits

Strava API has rate limits:
- **600 requests per 15 minutes**
- **30,000 requests per day**

The app automatically handles this by:
- Batching requests efficiently
- Showing progress for large datasets
- Graceful error handling

## Data Privacy

Your data stays on your computer:
- No data is sent to external servers
- Maps are generated locally
- Only connects to Strava's official API

## Next Steps

1. **Generate your first heatmap**:
   ```bash
   python generate_heatmaps.py --days 30
   ```

2. **Explore the web interface**:
   ```bash
   python app.py
   ```

3. **Customize and experiment**:
   - Try different time ranges
   - Compare speed vs elevation maps
   - Share your favorite routes

Enjoy mapping your cycling adventures! 🚴‍♂️🗺️
