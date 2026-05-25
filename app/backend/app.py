import os
import requests
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import json
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)
CORS(app)

# Prometheus metrics
weather_requests = Counter('weather_api_requests_total', 'Total weather API requests')
weather_errors = Counter('weather_api_errors_total', 'Total weather API errors')

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'postgres-service'),
        database=os.getenv('POSTGRES_DB', 'weatherdb'),
        user=os.getenv('POSTGRES_USER', 'weatheruser'),
        password=os.getenv('POSTGRES_PASSWORD', 'weatherpass')
    )

# Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis-service'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

API_KEY = os.getenv('OPENWEATHER_API_KEY')
API_BASE_URL = os.getenv('API_BASE_URL', 'https://api.openweathermap.org/data/2.5')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/metrics', methods=['GET'])
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/api/weather/<city>', methods=['GET'])
def get_weather(city):
    weather_requests.inc()
    print(f"Searching for city: {city}")
    
    # Try cache first
    cache_key = f"weather:{city.lower()}"
    cached = redis_client.get(cache_key)
    
    if cached:
        print(f"Cache hit for {city}")
        return jsonify(json.loads(cached))
    
    # Fetch from API
    url = f"{API_BASE_URL}/weather"
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric'
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code == 200:
            # Extract weather info
            weather_info = {
                'city': data['name'],
                'country': data['sys']['country'],
                'temperature': data['main']['temp'],
                'description': data['weather'][0]['description']
            }
            
            # Save to search history
            save_search_history(weather_info)
            
            # Cache for 10 minutes
            redis_client.setex(cache_key, 600, json.dumps(data))
            print(f"Saved weather for {city}")
            return jsonify(data)
        else:
            weather_errors.inc()
            print(f"Error: {data.get('message')}")
            return jsonify({'error': data.get('message', 'City not found')}), 404
    except Exception as e:
        weather_errors.inc()
        print(f"Exception: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id, city, country, temperature, description, search_time FROM search_history ORDER BY search_time DESC LIMIT 50")
        history = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(history)
    except Exception as e:
        print(f"History error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/favorites', methods=['GET'])
def get_favorites():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id, city, added_time FROM favorites ORDER BY added_time DESC")
        favorites = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(favorites)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/favorites', methods=['POST'])
def add_favorite():
    data = request.get_json()
    city = data.get('city')
    
    if not city:
        return jsonify({'error': 'City name required'}), 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO favorites (city) VALUES (%s) ON CONFLICT (city) DO NOTHING", (city,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Favorite added'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/favorites/<city>', methods=['DELETE'])
def remove_favorite(city):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM favorites WHERE city = %s", (city,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Favorite removed'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def save_search_history(weather_info):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO search_history (city, country, temperature, description) 
            VALUES (%s, %s, %s, %s)
        """, (weather_info['city'], weather_info['country'], weather_info['temperature'], weather_info['description']))
        conn.commit()
        print(f"Saved to history: {weather_info['city']}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error saving history: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)