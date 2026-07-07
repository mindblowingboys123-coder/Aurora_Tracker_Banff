import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # OpenWeatherMap API for weather data
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
    
    # Banff coordinates
    BANFF_LAT = 51.1784
    BANFF_LON = -115.5708
    
    # Cloud threshold for notifications (percentage)
    CLOUD_THRESHOLD = 50
    
    # Aurora monitoring settings
    AURORA_CHECK_INTERVAL = 300  # seconds (5 minutes)
    WEATHER_CHECK_INTERVAL = 600  # seconds (10 minutes)
