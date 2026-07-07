# 🌌 Banff Aurora Tracker

A real-time aurora borealis tracking website for Banff National Park with cloud coverage monitoring and viewing location recommendations.

## ✨ Features

- **Real-time Aurora Monitoring**: Tracks Kp index from NOAA Space Weather Prediction Center
- **Weather Integration**: Cloud coverage data from OpenWeatherMap API
- **Smart Notifications**: Real-time alerts when cloud coverage exceeds threshold
- **Viewing Locations**: Curated list of best spots in Banff for aurora viewing
- **Professional UI**: Clean, modern interface with dark space theme
- **WebSocket Updates**: Live data updates without page refresh
- **Responsive Design**: Works on desktop, tablet, and mobile

## 🚀 Quick Start

### Requirements
- Python 3.8+
- pip (comes with Python)

### Installation

```bash
# Navigate to project directory
cd /Users/Rishi/Documents/Newproject

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and add your API keys
cp .env.example .env
# Edit .env and add your OpenWeatherMap API key
```

### Get API Keys

1. **OpenWeatherMap API Key** (Required for weather data):
   - Sign up at https://openweathermap.org/api
   - Get a free API key
   - Add it to your `.env` file

2. **NOAA Aurora Data** (No API key required):
   - Uses public NOAA Space Weather API

### Running the Application

```bash
# Development mode
python app.py

# Production mode (with gunicorn)
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
```

Open your browser and navigate to `http://localhost:5000`

## 🎮 Usage

### Dashboard Features

1. **Aurora Activity Card**:
   - Shows current Kp index (0-9 scale)
   - Visibility probability percentage
   - Activity status (Low, Moderate, High)
   - Kp index of 5+ indicates good viewing conditions for Banff

2. **Cloud Coverage Card**:
   - Real-time cloud percentage
   - Status indicator (Clear, Partly Cloudy, Cloudy)
   - Automatic notifications when clouds exceed 50%

3. **Temperature Card**:
   - Current temperature in Celsius
   - Weather description
   - Helps plan for appropriate clothing

4. **Viewing Locations**:
   - 6 curated locations in Banff National Park
   - Ratings and light pollution levels
   - Detailed directions for each spot
   - Best photography spots highlighted

### Notification System

- **Cloud Alerts**: Automatic notifications when cloud coverage exceeds 50%
- **Rate Limited**: Notifications limited to once per hour to prevent spam
- **Real-time**: Uses WebSocket for instant updates

## 🔧 Technical Details

### Backend Architecture

- **Flask**: Web framework
- **Flask-SocketIO**: WebSocket support for real-time updates
- **NOAA API**: Aurora forecast data (Kp index)
- **OpenWeatherMap API**: Weather and cloud coverage data
- **Background Thread**: Continuous monitoring every 5 minutes

### Data Sources

1. **Aurora Data**: NOAA Space Weather Prediction Center
   - Planetary K-index
   - Updated every 3 hours by NOAA
   - Monitored every 5 minutes by app

2. **Weather Data**: OpenWeatherMap
   - Cloud coverage percentage
   - Temperature and conditions
   - Updated every 10 minutes by app

### Viewing Locations

The app includes 6 prime aurora viewing locations:

1. **Lake Louise** (5/5) - Iconic turquoise lake
2. **Moraine Lake** (5/5) - Valley of ten peaks
3. **Bow Lake** (4/5) - Icefields Parkway
4. **Peyto Lake** (4/5) - Glacial lake viewpoint
5. **Vermilion Lakes** (3/5) - Close to townsite
6. **Two Jack Lake** (3/5) - Quiet reflections

## � Deployment

### Domain Hosting

To host on your domain:

1. **Prepare for Production**:
```bash
# Set environment variables
export SECRET_KEY="your-production-secret-key"
export WEATHER_API_KEY="your-api-key"
```

2. **Using Gunicorn**:
```bash
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
```

3. **Using systemd** (Linux):
Create `/etc/systemd/system/aurora-tracker.service`:
```ini
[Unit]
Description=Aurora Tracker
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/app
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

4. **Nginx Reverse Proxy**:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

5. **SSL with Let's Encrypt**:
```bash
sudo certbot --nginx -d yourdomain.com
```

### Environment Variables

- `SECRET_KEY`: Flask secret key for sessions
- `WEATHER_API_KEY`: OpenWeatherMap API key

## 🔍 Configuration

### Adjust Cloud Threshold

Edit `config.py` to change the cloud notification threshold:

```python
CLOUD_THRESHOLD = 50  # Change this value (0-100)
```

### Adjust Check Intervals

Edit `config.py` to change monitoring frequency:

```python
AURORA_CHECK_INTERVAL = 300  # seconds (default: 5 minutes)
WEATHER_CHECK_INTERVAL = 600  # seconds (default: 10 minutes)
```

## 🛡️ Security

- Environment variables for sensitive data
- No hardcoded API keys
- CORS configuration for WebSocket
- Input validation on all endpoints

## 📝 License

MIT License - feel free to use this project for personal or commercial use.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Happy Aurora Hunting! 🌠**
