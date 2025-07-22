# Strava Activity Heatmap Generator 🚴‍♂️

Transform your Strava cycling data into stunning, interactive heatmaps! This Python project fetches your activity data via the Strava API and creates beautiful visualizations including speed-based heatmaps, elevation maps, and route overlays.

## 🌟 Features

- **Multiple Map Types:**
  - 🔥 **Basic Heatmap**: Overall activity density visualization
  - 🏃 **Speed Heatmap**: Color-coded by cycling speed (blue=slow, red=fast)
  - ⛰️ **Elevation Map**: Terrain-based coloring using elevation data
  - 🛣️ **Individual Routes**: Separate colored lines for each activity
  - 📊 **Activity Statistics**: Charts showing distance, speed, and time trends

- **Two Interfaces:**
  - 🌐 **Web Interface**: Beautiful Flask-based web app with interactive controls
  - 💻 **Command Line**: Simple CLI tool for batch generation

- **Smart Data Processing:**
  - OAuth2 authentication with Strava API
  - Automatic activity filtering (cycling only)
  - Configurable time ranges (30 days to 2 years)
  - GPS data validation and cleanup

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/chenrl129/strava-heatmap-generator.git
cd strava-heatmap-generator
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Strava API

1. Go to [Strava API Settings](https://www.strava.com/settings/api)
2. Create a new application
3. Copy your credentials to `.env`:

```env
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
STRAVA_ACCESS_TOKEN=your_access_token
```

### 4. Run the Application

**Web Interface:**
```bash
python app.py
```
Visit `http://localhost:5000` in your browser

**Command Line:**
```bash
python generate_heatmaps.py --days 365 --limit 50
```

## 🖥️ Web Interface

The web interface provides an intuitive way to generate and view your heatmaps:

### Features:
- **Athlete Dashboard**: View your Strava profile and activity statistics
- **Interactive Configuration**: Select time ranges, activity limits, and map types
- **Real-time Generation**: Watch your maps being created with progress updates
- **Embedded Viewing**: Preview maps directly in the browser
- **One-click Export**: Open full-screen versions in new tabs

### Screenshots:
- Clean, modern interface with gradient backgrounds
- Responsive design works on desktop and mobile
- Bootstrap-powered UI with smooth animations
- Real-time statistics and progress indicators

## 💻 Command Line Interface

For automation and batch processing:

```bash
# Generate all map types for the last year
python generate_heatmaps.py --days 365 --limit 100

# Generate only speed and elevation maps
python generate_heatmaps.py --maps speed elevation --days 180

# Custom output directory
python generate_heatmaps.py --output-dir my_maps --limit 25
```

### CLI Options:
- `--days`: Number of days back to fetch (default: 365)
- `--limit`: Maximum activities for detailed maps (default: 50)
- `--maps`: Map types to generate (default: all)
- `--output-dir`: Output directory (default: maps)

## 🗂️ Project Structure

```
strava-heatmap-generator/
├── src/
│   ├── strava_api.py          # Strava API client
│   └── heatmap_generator.py   # Map generation logic
├── templates/
│   └── index.html             # Web interface
├── static/                    # CSS/JS assets
├── maps/                      # Generated map outputs
├── app.py                     # Flask web application
├── generate_heatmaps.py       # CLI interface
├── requirements.txt           # Python dependencies
├── .env                       # API credentials
└── README.md                  # This file
```

## 🛠️ Technical Details

### Technologies Used:
- **Backend**: Python 3.7+, Flask
- **Mapping**: Folium (Leaflet.js), OpenStreetMap tiles
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib, Plotly
- **API Integration**: Requests, Strava API v3
- **Frontend**: Bootstrap 5, vanilla JavaScript

### Map Generation Process:
1. **Authentication**: OAuth2 token validation with Strava
2. **Data Fetching**: Retrieve activity summaries and GPS streams
3. **Data Processing**: Filter, clean, and validate GPS coordinates
4. **Visualization**: Generate interactive maps using Folium
5. **Export**: Save as HTML files with embedded JavaScript

### Performance Optimizations:
- **Selective Data Loading**: Only fetch GPS data for recent activities
- **Smart Sampling**: Reduce GPS point density for performance
- **Caching**: Store processed data to avoid re-computation
- **Async Processing**: Non-blocking map generation in web interface

## 🎨 Customization

### Map Styling:
- Modify color schemes in `heatmap_generator.py`
- Adjust point sizes and opacity for different effects
- Change base map tiles (OpenStreetMap, Satellite, etc.)

### Data Filters:
- Filter by activity type, distance, or duration
- Add weather data integration
- Include heart rate or power data visualization

### UI Themes:
- Customize Bootstrap theme in `templates/index.html`
- Add dark mode support
- Create mobile-first responsive layouts

## 🔧 Troubleshooting

### Common Issues:

**"Import folium could not be resolved"**
- Install dependencies: `pip install -r requirements.txt`

**"Missing Strava API credentials"**
- Check your `.env` file has all required variables
- Verify your Strava access token is valid

**"No activities found"**
- Ensure your Strava activities are public or you have proper permissions
- Check the date range - try increasing `--days` parameter

**Map generation is slow**
- Reduce the `--limit` parameter for fewer activities
- Check your internet connection for API calls

### Debug Mode:
```bash
# Enable Flask debug mode
export FLASK_DEBUG=True
python app.py

# Verbose CLI output
python generate_heatmaps.py --days 30 -v
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request with a clear description

### Development Setup:
```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Format code
black src/ app.py generate_heatmaps.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Strava API**: For providing comprehensive activity data
- **Folium**: For making interactive mapping accessible in Python
- **OpenStreetMap**: For beautiful, free map tiles
- **Bootstrap**: For responsive UI components

## 🔗 Links

- [Strava API Documentation](https://developers.strava.com/)
- [Folium Documentation](https://python-visualization.github.io/folium/)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

**Happy Mapping!** 🗺️✨

Transform your cycling adventures into beautiful visualizations and discover new insights about your riding patterns!
