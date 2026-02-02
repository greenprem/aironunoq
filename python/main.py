import os
import time
import threading
import numpy as np
import cv2
import tensorflow as tf
from flask import Flask, jsonify

# --- CONFIGURATION ---
MODEL_PATH = "../assets/fog_model.keras"
IMG_SIZE = (224, 224)
CAMERA_INDEX = 0  # Usually /dev/video0
latest_fog_result = {"score": 0.0, "label": "Initializing...", "timestamp": 0}

app = Flask(__name__)

# --- MODEL LOADING ---
def load_fog_model():
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Model file not found at {MODEL_PATH}")
        return None
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        print("✅ TensorFlow model loaded successfully.")
        return model
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None

model = load_fog_model()

# --- CAMERA & INFERENCE LOOP ---
def camera_inference_worker():
    global latest_fog_result

    # Initialize Linux Video Capture
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"❌ Could not open video device /dev/video{CAMERA_INDEX}")
        return

    print(f"📸 Camera thread active. Scoring every 10 seconds...")

    while True:
        ret, frame = cap.read()
        if ret:
            try:
                # 1. Preprocess the frame (OpenCV uses BGR, TF uses RGB)
                img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img_resized = cv2.resize(img_rgb, IMG_SIZE)

                arr = tf.keras.applications.mobilenet_v2.preprocess_input(img_resized)
                arr = np.expand_dims(arr, axis=0)

                # 2. Run Inference
                score = float(model.predict(arr, verbose=0)[0][0])
                label = "Foggy" if score > 0.5 else "Non-Foggy"

                # 3. Update Global State
                latest_fog_result = {
                    "score": round(score, 4),
                    "label": label,
                    "timestamp": time.ctime()
                }
                print(f"[{latest_fog_result['timestamp']}] Score: {score:.4f} ({label})")

            except Exception as e:
                print(f"Inference Error: {e}")
        else:
            print("❌ Failed to grab frame from camera.")

        # Wait for 10 seconds before the next capture
        time.sleep(10)

    cap.release()

# --- API ROUTES ---
@app.route('/api/fog')
def get_fog_status():
    return jsonify(latest_fog_result)

if __name__ == "__main__":
    if model is not None:
        # Start the background thread
        threading.Thread(target=camera_inference_worker, daemon=True).start()

        # Start the Flask server
        # Access from PC at http://192.168.189.129:8080/api/fog
        print("🚀 Fog API Server starting on port 8080...")
        app.run(host='0.0.0.0', port=8084)
