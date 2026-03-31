"""
Face Recognition Attendance Web App
Flask backend: registration, recognition, attendance log API
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import face_recognition
import numpy as np
import base64
import cv2
import os
import csv
import json
from datetime import datetime
from pathlib import Path
import io

app = Flask(__name__)
CORS(app)

KNOWN_FACES_DIR = Path("known_faces")
ATTENDANCE_LOG  = Path("attendance.csv")
ENCODINGS_FILE  = Path("encodings.json")

KNOWN_FACES_DIR.mkdir(exist_ok=True)

# ── in-memory store ────────────────────────────────────────────
known_encodings = []
known_names     = []
attendance_today = {}   # name -> time string

def save_encodings():
    data = [
        {"name": name, "encoding": enc.tolist()}
        for name, enc in zip(known_names, known_encodings)
    ]
    with open(ENCODINGS_FILE, "w") as f:
        json.dump(data, f)

def load_encodings():
    global known_encodings, known_names
    known_encodings.clear()
    known_names.clear()
    if ENCODINGS_FILE.exists():
        with open(ENCODINGS_FILE) as f:
            for item in json.load(f):
                known_names.append(item["name"])
                known_encodings.append(np.array(item["encoding"]))
    print(f"[INFO] Loaded {len(known_names)} encodings for {len(set(known_names))} people.")

def init_log():
    if not ATTENDANCE_LOG.exists():
        with open(ATTENDANCE_LOG, "w", newline="") as f:
            csv.writer(f).writerow(["Name","Date","Time","Status"])

def decode_image(data_url: str) -> np.ndarray:
    header, encoded = data_url.split(",", 1)
    img_bytes = base64.b64decode(encoded)
    arr = np.frombuffer(img_bytes, np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)

# ── routes ─────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    name   = data.get("name", "").strip()
    images = data.get("images", [])   # list of base64 data-URLs

    if not name or not images:
        return jsonify({"success": False, "error": "Name and images required"}), 400

    person_dir = KNOWN_FACES_DIR / name
    person_dir.mkdir(exist_ok=True)

    added = 0
    for i, img_url in enumerate(images):
        try:
            frame = decode_image(img_url)
            rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            encs  = face_recognition.face_encodings(rgb)
            if not encs:
                continue
            ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            cv2.imwrite(str(person_dir / f"{name}_{ts}.jpg"), frame)
            known_encodings.append(encs[0])
            known_names.append(name)
            added += 1
        except Exception as e:
            print(f"[WARN] frame {i}: {e}")

    if added == 0:
        return jsonify({"success": False, "error": "No face detected in any image"}), 400

    save_encodings()
    return jsonify({"success": True, "message": f"Registered '{name}' with {added} samples.",
                    "total_people": len(set(known_names))})

@app.route("/api/recognize", methods=["POST"])
def recognize():
    data     = request.json
    img_url  = data.get("image")
    tolerance = float(data.get("tolerance", 0.5))

    if not img_url:
        return jsonify({"success": False, "error": "No image provided"}), 400

    frame = decode_image(img_url)
    rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    small = cv2.resize(rgb, (0, 0), fx=0.5, fy=0.5)

    locations = face_recognition.face_locations(small)
    encodings = face_recognition.face_encodings(small, locations)

    results = []
    for (top, right, bottom, left), enc in zip(locations, encodings):
        name  = "Unknown"
        match = False
        if known_encodings:
            distances = face_recognition.face_distance(known_encodings, enc)
            best      = int(np.argmin(distances))
            if distances[best] < tolerance:
                name  = known_names[best]
                match = True
                _mark(name)

        inv = 2
        results.append({
            "name": name, "match": match,
            "box": {"top": top*inv, "right": right*inv,
                    "bottom": bottom*inv, "left": left*inv}
        })

    return jsonify({"success": True, "faces": results,
                    "present_today": list(attendance_today.keys())})

def _mark(name: str):
    if name not in attendance_today:
        now = datetime.now()
        attendance_today[name] = now.strftime("%H:%M:%S")
        with open(ATTENDANCE_LOG, "a", newline="") as f:
            csv.writer(f).writerow([name, now.strftime("%Y-%m-%d"),
                                    now.strftime("%H:%M:%S"), "Present"])

@app.route("/api/attendance")
def attendance():
    date = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
    rows = []
    if ATTENDANCE_LOG.exists():
        with open(ATTENDANCE_LOG) as f:
            for r in csv.DictReader(f):
                if r["Date"] == date:
                    rows.append(r)
    return jsonify({"date": date, "records": rows,
                    "live_present": attendance_today})

@app.route("/api/people")
def people():
    return jsonify({"people": sorted(set(known_names)),
                    "total": len(set(known_names))})

@app.route("/api/reset_session", methods=["POST"])
def reset_session():
    attendance_today.clear()
    return jsonify({"success": True})

if __name__ == "__main__":
    init_log()
    load_encodings()
    app.run(debug=True, port=5000)