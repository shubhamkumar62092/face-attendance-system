# Face Attendance system Web App

A full-stack web application that lets you register people via webcam and automatically mark attendance using facial recognition. Built with Flask (Python backend) and vanilla HTML/CSS/JS (frontend).

---

## Features

- **Register** — open webcam, capture 3–5 photos, register a person with one click
- **Recognize** — live webcam feed with real-time face detection and green/red bounding boxes
- **Attendance** — automatic CSV logging; filter by date; live stats dashboard
- **Adjustable tolerance** — slider to tune recognition strictness per environment

---

## Project Structure

```
face-attendance-web/
├── app.py               # Flask backend (API routes)
├── index.html           # Full frontend (single file)
├── requirements.txt     # Python dependencies
├── known_faces/         # Auto-created; stores registration photos
│   └── <Name>/
│       └── photo_001.jpg
├── attendance.csv       # Auto-generated attendance log
└── encodings.json       # Cached face encodings (auto-generated)
```

---

## Setup

### 1. Install system dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update && sudo apt-get install cmake libopenblas-dev liblapack-dev build-essential
```

**macOS:**
```bash
brew install cmake
```

**Windows:** Install [CMake](https://cmake.org/download/) and add to PATH.

### 2. Install Python packages

```bash
pip install -r requirements.txt
```

> dlib takes 5–10 minutes to compile. This is normal.

### 3. Run the app

```bash
python app.py
```

Open `index.html` in your browser (double-click it, or serve with VS Code Live Server).

---

## How to Use

### Register a Person
1. Go to the **Register** tab
2. Type the person's full name
3. Click **Open Camera**
4. Click **Capture Photo** 3–5 times (different angles)
5. Click **Register**

### Take Attendance
1. Go to the **Recognize** tab
2. Click **Start**
3. The system detects faces automatically — green box = recognized, red = unknown
4. Attendance is logged instantly; view the **Present Today** panel on the right

### View Attendance Log
1. Go to the **Attendance** tab
2. Select any date using the date picker
3. See who was present, along with timestamps and stats

---

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/register` | Register a person with base64 images |
| POST | `/api/recognize` | Recognize faces in a single frame |
| GET  | `/api/attendance?date=YYYY-MM-DD` | Get attendance records |
| GET  | `/api/people` | List all registered people |
| POST | `/api/reset_session` | Clear today's in-memory attendance |

---

## Tolerance Guide

| Value | Effect |
|-------|--------|
| 0.40 | Very strict — fewer false positives |
| 0.50 | Default — good for indoor use |
| 0.60 | Lenient — better in varied lighting |

---

## Technologies

| Tool | Role |
|------|------|
| Flask | Python web server and REST API |
| flask-cors | Allow browser to call the API |
| face_recognition | Face encoding and matching |
| OpenCV | Image decoding and processing |
| dlib | HOG detector and ResNet encoder |
| HTML/CSS/JS | Full frontend, no frameworks |

---

*Computer Vision Course — BYOP Project*
