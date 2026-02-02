# Fog & Environment Monitoring System

This project is a comprehensive monitoring solution that combines computer vision and hardware sensors to detect fog, smoke, and environmental conditions. It uses **Deep Learning (MobileNetV2)** for visual analysis and an **Arduino/Modulino** setup for physical sensing (PM2.5, Temperature).

## 📂 Repository Structure

```
├── python/
│   ├── main.py          # Vision System (Flask API + TensorFlow Analysis)
│   ├── mq_py_api.py     # Sensor Bridge API (Flask interface for Arduino)
│   └── read.py          # Dashboard CLI (Aggregates data from both APIs)
├── sketch/
│   └── sketch.ino       # Arduino Firmware (PM2.5 + Temperature reading)
├── assets/
│   ├── fog_model.keras  # Pre-trained Fog Detection Model
│   └── (images/etc)
├── 3d_print/            # Enclosure designs (STL)
├── app.yaml             # Deployment configuration
├── requirements.txt     # Python dependencies
├── setup_repo.sh        # Linux/WSL Setup Script
├── setup_repo.bat       # Windows Setup Script
└── LICENSE.txt          # Mozilla Public License 2.0
```

## 🛠️ Hardware Requirements

1.  **Host Computer**: Arduino UNO Q.
2.  **Microcontroller**: Arduino UNO Q Board (compatible with `Arduino_RouterBridge` and Portenta/Modulino carrier).
3.  **Sensors**:
    *   **PMS7003**: Particulate Matter sensor (PM2.5).
    *   **NTC Thermistor**: For temperature sensing (connected to Analog Pin A0).
4.  **Camera**: USB Webcam or Raspberry Pi Camera (mapped to `/dev/video0`).

## 🚀 Installation Guide

### Phase 1: Firmware (Arduino)
1.  Open `sketch/sketch.ino` in the Arduino IDE.
2.  Install the required library: **Arduino_RouterBridge**.
3.  Connect your Arduino board.
4.  Select the correct Port and Board type.
5.  **Upload** the sketch.

### Phase 2: Host Software (Linux)

1.  **Environment Setup**:
    It is recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    # venv\Scripts\activate   # Windows
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 🏃 Usage

The system consists of three components that run simultaneously. You may want to run them in separate terminals or using a process manager (like `systemd` or `supervisord`).

### 1. Start the Vision System
This service captures video, runs the fog detection model, and exposes the data.
```bash
cd python
python main.py
```
*   **Port**: 8084
*   **Endpoint**: `/api/fog`

### 2. Start the Sensor Bridge
This service communicates with the Arduino/MCU hardware via the Bridge architecture.
```bash
cd python
python mq_py_api.py
```
*   **Port**: 8085
*   **Endpoints**: `/api/pm25`, `/api/temp`

### 3. Run the Dashboard
This script aggregates data from the above two services and prints a real-time status report to your terminal.
```bash
cd python
python read.py
```

## 📊 Sample Output
```text
==================================================
📊 SYSTEM MONITORING REPORT | Mon Feb  2 23:30:00 2026
==================================================

📷 Camera Vision System:
   - Status: NON-FOGGY
   - Confidence Score: 0.1245
   - Analysis: ✅ VISIBILITY CLEAR - No significant obstruction.

🌱 Environmental Sensors:
   - Particulate Matter (PM2.5): 10 µg/m³ (Good)
   - Temperature: 24.5 °C

==================================================
```

![Dashboard](assets/dashboard.png)


## 📜 License
This software is licensed under the **Mozilla Public License Version 2.0**. See the [LICENSE.txt](LICENSE.txt) file for full details.
