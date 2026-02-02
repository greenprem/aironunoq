import requests
import time
import sys

# Configuration
FOG_API_URL = "http://localhost:8084/api/fog"
SENSOR_PM25_URL = "http://localhost:8085/api/pm25"
SENSOR_TEMP_URL = "http://localhost:8085/api/temp"

def fetch_data(url, label):
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Status {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"error": "Connection Refused (Is the service running?)"}
    except Exception as e:
        return {"error": str(e)}

def print_status_report():
    print("\n" + "="*50)
    print(f"📊 SYSTEM MONITORING REPORT | {time.ctime()}")
    print("="*50)

    # 1. Fog Detection
    fog_data = fetch_data(FOG_API_URL, "Fog Camera")
    if "error" not in fog_data:
        score = fog_data.get('score', 0)
        label = fog_data.get('label', 'Unknown')
        print(f"\n📷 Camera Vision System:")
        print(f"   - Status: {label.upper()}")
        print(f"   - Confidence Score: {score:.4f}")
        
        if score > 0.6:
            desc = "⚠️ VISIBILITY LOW - Fog/Smoke detected!"
        else:
            desc = "✅ VISIBILITY CLEAR - No significant obstruction."
        print(f"   - Analysis: {desc}")
    else:
        print(f"\n📷 Camera Vision System: ❌ OFFLINE ({fog_data['error']})")

    # 2. Environmental Sensors
    print(f"\n🌱 Environmental Sensors:")
    
    # PM2.5
    pm_data = fetch_data(SENSOR_PM25_URL, "PM2.5")
    if "error" not in pm_data and "value" in pm_data:
        val = pm_data['value']
        unit = pm_data.get('unit', '')
        
        # AQI basic interpretation
        if val < 12: quality = "Good"
        elif val < 35: quality = "Moderate"
        else: quality = "Unhealthy"
        
        print(f"   - Particulate Matter (PM2.5): {val} {unit} ({quality})")
    else:
        print(f"   - Particulate Matter (PM2.5): ⚠️ Unavailable")

    # Temperature
    temp_data = fetch_data(SENSOR_TEMP_URL, "Temperature")
    if "error" not in temp_data and "value" in temp_data:
        val = temp_data['value']
        unit = temp_data.get('unit', '°C')
        print(f"   - Temperature: {val:.1f} {unit}")
    else:
        print(f"   - Temperature: ⚠️ Unavailable")

    print("\n" + "="*50)

if __name__ == "__main__":
    while True:
        try:
            print_status_report()
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped.")
            sys.exit(0)