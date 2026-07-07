from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import requests
import threading
import time
import os
from datetime import datetime
from config import Config

app = Flask(__name__, template_folder='templates')
app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
current_aurora_data = {}
current_weather_data = {}
last_cloud_notification = None

# Banff viewing locations
VIEWING_LOCATIONS = [
    {
        "name": "Lake Louise",
        "description": "Iconic turquoise lake with mountain reflections. Best for aurora photography.",
        "directions": "Drive west on Trans-Canada Hwy, take Lake Louise Drive exit. Park at lakeside lot.",
        "lat": 51.4227,
        "lon": -116.1775,
        "rating": 5,
        "light_pollution": "Low"
    },
    {
        "name": "Moraine Lake",
        "description": "Stunning valley of ten peaks. Limited access, check road status.",
        "directions": "Continue past Lake Louise, follow Moraine Lake Road. Shuttle required in peak season.",
        "lat": 51.3242,
        "lon": -116.1815,
        "rating": 5,
        "light_pollution": "Very Low"
    },
    {
        "name": "Bow Lake",
        "description": "Less crowded, beautiful reflections. Icefields Parkway.",
        "directions": "North on Icefields Parkway (Hwy 93). Parking available at Bow Lake viewpoint.",
        "lat": 51.6800,
        "lon": -116.4700,
        "rating": 4,
        "light_pollution": "Very Low"
    },
    {
        "name": "Peyto Lake",
        "description": "Glacial lake with unique shape. Short hike from parking.",
        "directions": "Icefields Parkway, Peyto Lake exit. 1km hike to viewpoint.",
        "lat": 51.7167,
        "lon": -116.5000,
        "rating": 4,
        "light_pollution": "Very Low"
    },
    {
        "name": "Vermilion Lakes",
        "description": "Close to Banff townsite. Easy access, multiple lakes.",
        "directions": "Mount Norquay Road, just west of Banff. Multiple pullouts along the road.",
        "lat": 51.1850,
        "lon": -115.6150,
        "rating": 3,
        "light_pollution": "Low"
    },
    {
        "name": "Two Jack Lake",
        "description": "Quiet lake near Johnson Lake. Good for reflections.",
        "directions": "Lake Minnewanka Loop Road, past Johnson Lake.",
        "lat": 51.2050,
        "lon": -115.5350,
        "rating": 3,
        "light_pollution": "Low"
    }
]

def get_aurora_forecast():
    """Get aurora forecast from NOAA"""
    try:
        # NOAA Space Weather Prediction Center API
        url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Get the most recent Kp index
        if len(data) > 1:
            latest = data[1]
            kp_index = float(latest[1])
            
            # Calculate aurora visibility probability
            # Kp index of 5+ is good for Banff (magnetic latitude ~55-60)
            visibility_probability = min(100, (kp_index / 9) * 100)
            
            return {
                "kp_index": kp_index,
                "visibility_probability": visibility_probability,
                "timestamp": latest[0],
                "status": "Active" if kp_index >= 4 else "Low Activity"
            }
    except Exception as e:
        print(f"Error fetching aurora data: {e}")
    
    return {
        "kp_index": 0,
        "visibility_probability": 0,
        "timestamp": datetime.now().isoformat(),
        "status": "Unknown"
    }

def get_weather_data():
    """Get weather data from OpenWeatherMap"""
    if not app.config['WEATHER_API_KEY']:
        return {
            "cloud_coverage": 0,
            "temperature": 0,
            "description": "API key not configured",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": app.config['BANFF_LAT'],
            "lon": app.config['BANFF_LON'],
            "appid": app.config['WEATHER_API_KEY'],
            "units": "metric"
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        return {
            "cloud_coverage": data.get('clouds', {}).get('all', 0),
            "temperature": data.get('main', {}).get('temp', 0),
            "description": data.get('weather', [{}])[0].get('description', ''),
            "humidity": data.get('main', {}).get('humidity', 0),
            "wind_speed": data.get('wind', {}).get('speed', 0),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error fetching weather data: {e}")
    
    return {
        "cloud_coverage": 0,
        "temperature": 0,
        "description": "Error fetching data",
        "timestamp": datetime.now().isoformat()
    }

def check_and_notify_clouds():
    """Check cloud coverage and send notification if above threshold"""
    global last_cloud_notification
    
    cloud_coverage = current_weather_data.get('cloud_coverage', 0)
    threshold = app.config['CLOUD_THRESHOLD']
    
    if cloud_coverage > threshold:
        notification = {
            "type": "cloud_warning",
            "message": f"Cloud coverage is {cloud_coverage}% - aurora visibility may be reduced",
            "cloud_coverage": cloud_coverage,
            "timestamp": datetime.now().isoformat()
        }
        
        # Only notify if we haven't sent a notification in the last hour
        if (last_cloud_notification is None or 
            (datetime.now() - datetime.fromisoformat(last_cloud_notification)).seconds > 3600):
            socketio.emit('notification', notification)
            last_cloud_notification = notification['timestamp']
            print(f"Cloud notification sent: {cloud_coverage}%")

def background_monitor():
    """Background thread to monitor aurora and weather conditions"""
    while True:
        # Update aurora data
        global current_aurora_data
        current_aurora_data = get_aurora_forecast()
        socketio.emit('aurora_update', current_aurora_data)
        
        # Update weather data
        global current_weather_data
        current_weather_data = get_weather_data()
        socketio.emit('weather_update', current_weather_data)
        
        # Check for cloud warnings
        check_and_notify_clouds()
        
        print(f"Updated: Aurora Kp={current_aurora_data.get('kp_index', 0)}, "
              f"Clouds={current_weather_data.get('cloud_coverage', 0)}%")
        
        time.sleep(app.config['AURORA_CHECK_INTERVAL'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/aurora')
def get_aurora():
    return jsonify(current_aurora_data)

@app.route('/api/weather')
def get_weather():
    return jsonify(current_weather_data)

@app.route('/api/locations')
def get_locations():
    return jsonify(VIEWING_LOCATIONS)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Fetch fresh data on connection
    global current_aurora_data, current_weather_data
    current_aurora_data = get_aurora_forecast()
    current_weather_data = get_weather_data()
    emit('aurora_update', current_aurora_data)
    emit('weather_update', current_weather_data)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    # Start background monitoring thread
    monitor_thread = threading.Thread(target=background_monitor, daemon=True)
    monitor_thread.start()
    
    port = int(os.environ.get('PORT', 5001))
    socketio.run(app, debug=False, host='0.0.0.0', port=port)
