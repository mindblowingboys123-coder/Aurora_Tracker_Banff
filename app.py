from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import os
from dotenv import load_dotenv
from datetime import datetime
import logging
from data.locations import BANFF_LOCATIONS
from services.aurora_service import AuroraService
from services.weather_service import WeatherService

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=60, ping_interval=25)

aurora_service = AuroraService()
weather_service = WeatherService()

cloud_thresholds = {location['id']: 50 for location in BANFF_LOCATIONS}
cloud_history = {location['id']: [] for location in BANFF_LOCATIONS}
connected_users = set()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/locations')
def get_locations():
    return jsonify(BANFF_LOCATIONS)

@app.route('/api/current-conditions')
def get_current_conditions():
    try:
        conditions = []
        for location in BANFF_LOCATIONS:
            weather = weather_service.get_weather(location['lat'], location['lon'])
            aurora = aurora_service.get_aurora_forecast(location['lat'], location['lon'])
            conditions.append({
                'location_id': location['id'],
                'location_name': location['name'],
                'weather': weather,
                'aurora': aurora,
                'timestamp': datetime.utcnow().isoformat()
            })
        return jsonify(conditions)
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

def check_aurora_conditions():
    try:
        for location in BANFF_LOCATIONS:
            weather = weather_service.get_weather(location['lat'], location['lon'])
            aurora = aurora_service.get_aurora_forecast(location['lat'], location['lon'])
            cloud_cover = weather.get('cloud_cover', 100)
            location_id = location['id']
            
            cloud_history[location_id].append({
                'timestamp': datetime.utcnow().isoformat(),
                'cloud_cover': cloud_cover
            })
            
            if len(cloud_history[location_id]) > 1440:
                cloud_history[location_id].pop(0)
            
            if cloud_cover > cloud_thresholds[location_id]:
                socketio.emit('cloud_alert', {
                    'location_id': location_id,
                    'location_name': location['name'],
                    'cloud_cover': cloud_cover,
                    'threshold': cloud_thresholds[location_id],
                    'message': f"⚠️ Cloud cover at {location['name']} is now {cloud_cover}%",
                    'timestamp': datetime.utcnow().isoformat(),
                    'weather': weather,
                    'aurora': aurora
                }, broadcast=True)
            
            socketio.emit('location_update', {
                'location_id': location_id,
                'location_name': location['name'],
                'cloud_cover': cloud_cover,
                'weather': weather,
                'aurora': aurora,
                'timestamp': datetime.utcnow().isoformat()
            }, broadcast=True)
    except Exception as e:
        logger.error(f"Background job error: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(func=check_aurora_conditions, trigger="interval", minutes=5)
scheduler.start()

@socketio.on('connect')
def handle_connect():
    connected_users.add(request.sid)
    logger.info(f"Connected: {len(connected_users)} users")
    emit('connection_response', {'data': 'Connected'})

@socketio.on('disconnect')
def handle_disconnect():
    connected_users.discard(request.sid)
    logger.info(f"Disconnected: {len(connected_users)} users")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)