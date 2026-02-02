import sys
import os
from flask import Flask, jsonify

# 1. Path & Socket Setup
# Point to your extracted library folder (Adjust path as needed for your specific environment)
sys.path.append('/home/arduino/ArduinoApps/copy-of-blink-led-with-uilibcp1/arduino_lib_extracted')
# Direct link to the hardware router
os.environ["ARDUINO_ROUTER_SOCKET"] = "/var/run/arduino-router.sock"

# 2. Import the Bridge
try:
    from arduino.app_utils import Bridge
    print("✅ Hardware Bridge logic loaded.")
except ImportError as e:
    print(f"❌ Library error: {e}")
    sys.exit(1)

# 3. Standard Flask App
app = Flask(__name__)

@app.route('/api/pm25')
def get_pm25():
    try:
        val = Bridge.call("read_pm25")
        if val is not None and isinstance(val, int) and val >= 0:
            return jsonify({"sensor": "PM2.5", "value": val, "unit": "µg/m³", "status": "success"})
        else:
            return jsonify({"error": "Sensor Read Error or No Data"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/temp')
def get_temp():
    try:
        # Bridge returns int (degrees * 100). Convert back to float.
        val = Bridge.call("read_temperature")
        if val is not None and isinstance(val, int) and val > -900:
            temp_c = val / 100.0
            return jsonify({"sensor": "Temperature", "value": temp_c, "unit": "°C", "status": "success"})
        else:
            return jsonify({"error": "Sensor Read Error"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("🚀 Sensor API starting on http://0.0.0.0:8085")
    app.run(host='0.0.0.0', port=8085)