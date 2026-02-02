from flask import Flask, render_template, jsonify
import requests
import time
import threading
import sys
import collections

# Configuration
FOG_API_URL = "http://localhost:8084/api/fog"
SENSOR_PM25_URL = "http://localhost:8085/api/pm25"
SENSOR_TEMP_URL = "http://localhost:8085/api/temp"
HISTORY_LEN = 50

# Global State
history = collections.deque(maxlen=HISTORY_LEN)
latest_snapshot = {
    "fog": {},
    "pm25": {},
    "temp": {},
    "timestamp": 0
}

app = Flask(__name__)

# --- Data Fetching Logic (Background Thread) ---
def fetch_data(url):
    try:
        response = requests.get(url, timeout=1)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {"error": "Offline"}

def monitor_loop():
    global latest_snapshot
    while True:
        try:
            timestamp = time.time()
            time_str = time.ctime(timestamp)
            
            # Fetch all data
            fog = fetch_data(FOG_API_URL)
            pm25 = fetch_data(SENSOR_PM25_URL)
            temp = fetch_data(SENSOR_TEMP_URL)
            
            # Update Snapshot
            latest_snapshot = {
                "fog": fog,
                "pm25": pm25,
                "temp": temp,
                "timestamp": timestamp,
                "time_str": time_str
            }
            
            # Append to History (only if some data is valid)
            history.append(latest_snapshot)
            
            # Console Log (As requested, keeping existing legacy behavior)
            print_status_report(latest_snapshot)
            
            time.sleep(5)
        except Exception as e:
            print(f"Monitor Error: {e}")
            time.sleep(5)

def print_status_report(snap):
    print("\n" + "="*50)
    print(f"📊 MONITORING | {snap['time_str']}")
    print("="*50)
    
    # Fog
    f = snap['fog']
    if "error" not in f:
        print(f"📷 Camera: {f.get('label','?')} ({f.get('score',0):.2f})")
    else:
        print("📷 Camera: OFFLINE")

    # Sensors
    p = snap['pm25']
    t = snap['temp']
    
    p_val = f"{p.get('value')} {p.get('unit')}" if "value" in p else "Unavailable"
    t_val = f"{t.get('value')} {t.get('unit')}" if "value" in t else "Unavailable"
    
    print(f"🌱 PM2.5: {p_val}")
    print(f"🌡️ Temp:  {t_val}")
    print("="*50)

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/history')
def get_history():
    return jsonify(list(history))

@app.route('/api/status')
def get_status():
    return jsonify(latest_snapshot)

if __name__ == "__main__":
    # Start background thread
    t = threading.Thread(target=monitor_loop, daemon=True)
    t.start()
    
    print("🌍 Dashboard started at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000)
