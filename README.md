# VisionX Guide 👁️🎙️

### AI-Powered Assistive Object Awareness Prototype

**VisionX Guide** is a Python-based assistive technology prototype designed to explore how real-time object detection and spoken feedback could support people with visual impairments. It analyzes a live camera feed, identifies selected objects, estimates their **relative position in the camera frame** (left, center, or right), and provides voice alerts.

> **Prototype status:** A working demonstration, **not a validated navigation or obstacle-avoidance aid**. It cannot determine safe paths, reliably estimate distance, or replace a white cane, guide dog, mobility training, or human assistance.

## ✨ Features

- **Real-time object detection** using Ultralytics YOLO11n.
- **Position-based alerts** identifying objects on the left, center, or right side of the camera view.
- **Spoken feedback** using `edge-tts` and `pygame`, with balanced Hinglish-style alerts.
- **Basic voice commands** using Python's `SpeechRecognition` library.
- **Alert management** with confidence filtering and cooldowns to help reduce repeated announcements.
- **Camera input** from a laptop webcam or a connected mobile-phone camera via iVCam.

## 🧠 Technology Stack

| Component | Technology |
| --- | --- |
| Programming language | Python |
| Object detection | Ultralytics YOLO11n |
| Video processing | OpenCV |
| Speech synthesis | edge-tts + pygame |
| Voice input | SpeechRecognition |
| Development environment | Windows, CPU-based prototype |

## ⚙️ How It Works

1. OpenCV reads frames from the selected camera.
2. YOLO11n detects objects and returns bounding boxes and confidence scores.
3. For selected detections, the application compares the object's horizontal center with the frame width to identify **left**, **center**, or **right**.
4. The alert manager filters messages and limits frequent repetitions.
5. The speech manager announces relevant object information aloud.
6. A separate voice-command handler listens for supported commands, including a stop/exit command.

**Important:** Left/center/right describes the object's position **in the image**, not a verified safe direction to move. Apparent object size is not a reliable measurement of distance.

## 📁 Project Structure

```text
VisionX-Guide/
├── smart_guide.py             # Main camera and detection pipeline
├── yolo11n.pt                 # YOLO model weights (downloaded separately if absent)
├── visionx/
│   ├── __init__.py
│   ├── alerts.py              # Alert selection and cooldown logic
│   ├── speech.py              # Voice feedback
│   └── voice_commands.py      # Microphone input and commands
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10+ (use a version compatible with your installed packages)
- A functioning camera and, for voice commands, a microphone
- Speakers or headphones
- Internet access for online speech/recognition services where required

### Installation (Windows PowerShell)

```powershell
# 1. Clone your repository
# git clone https://github.com/YOUR-USERNAME/VisionX-Guide.git
# cd VisionX-Guide

# 2. Create and activate a virtual environment
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install core dependencies
python -m pip install --upgrade pip
pip install ultralytics opencv-python edge-tts pygame SpeechRecognition
```

Microphone support may also require a compatible audio input package such as `PyAudio`, depending on your environment. Refer to your tested environment configuration for the exact requirements.

### Run

```powershell
python smart_guide.py
```

Set the camera index in `smart_guide.py` to match your webcam or iVCam device. The YOLO model file (`yolo11n.pt`) must be available to the model loader; Ultralytics may download it when first used.

> **Deployment note:** Dependency versions and device behavior can vary. Before publishing installation instructions as fully reproducible, export the packages from the working environment into `requirements.txt` and verify a clean installation.

## 🧪 Development and Testing

The prototype has been developed incrementally with a focus on getting object detection, spoken feedback, and voice commands working together. Further evaluation is required to measure:

- Correct and missed detections under different lighting and camera conditions
- False alerts and repeated alerts
- Alert latency and the clarity of spoken messages
- Performance on everyday objects, including small or partially hidden objects
- Accessibility and usability with expert guidance

**No validated accuracy, distance accuracy, or navigation safety metrics are claimed.**

## 🛣️ Future Roadmap

- [x] Camera-based object detection prototype
- [x] Relative position cues (left / center / right)
- [x] Spoken object alerts
- [x] Basic voice commands
- [ ] More systematic detection and usability evaluation
- [ ] Destination understanding and GPS-based route guidance experiments
- [ ] Explore a mapping API for spoken directions
- [ ] Explore portable hardware and mobile integration
- [ ] Conduct supervised, consent-based usability studies with mobility specialists and visually impaired participants

## 🤝 Motivation

VisionX Guide began as a student innovation project focused on exploring accessible, voice-first technology. The goal is to learn from practical testing and user feedback, and investigate how computer vision might **complement**, rather than replace, established mobility tools.

## 👨‍💻 Project Development

**Saksham Shrivastav**  
B.Tech — Computer Science and Engineering (AI/ML)  
BBS College of Engineering and Technology, Prayagraj

*Developed as a student-led prototype. This repository documents ongoing experimentation and learning.*

---

⭐ If you find this project interesting, feel free to explore the code and follow its progress.
