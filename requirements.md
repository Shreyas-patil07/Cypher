# Requirements Document: CYPHER - AI Surveillance Intelligence System

## Project Overview

CYPHER is an AI-powered surveillance system designed for hackathon demonstration. It detects security threats in real-time from video feeds using YOLOv8 object detection, with a focus on demo-readiness and professional presentation.

**Tagline:** Real-time Threat Detection Powered by AI

**Scope:** Hackathon prototype (not production-scale)

---

## 1. Functional Requirements

### 1.1 Video Input Processing

**1.1.1** The system SHALL accept video input from webcam, CCTV stream, or video file.

**1.1.2** The system SHALL capture frames from the video source using OpenCV VideoCapture.

**1.1.3** The system SHALL implement frame skipping (process every 2nd frame) to optimize performance.

**1.1.4** The system SHALL resize captured frames to 640x640 pixels for YOLO inference.

**1.1.5** The system SHALL maintain original frame dimensions for coordinate mapping of detections.

### 1.2 Object Detection

**1.2.1** The system SHALL use YOLOv8n model for object detection.

**1.2.2** The system SHALL detect persons and vehicles in video frames using COCO dataset classes.

**1.2.3** The system SHALL filter detections by confidence threshold (default 0.5).

**1.2.4** The system SHALL return structured detection results with bounding boxes, class names, and confidence scores.

**CRITICAL NOTE:** YOLOv8n with COCO dataset does NOT include "knife" or "gun" classes. Weapon detection requires:
- Custom trained model with weapon classes, OR
- Simulated weapon detection for demo purposes (detect "person" + random weapon classification)

### 1.3 Person Detection (Primary Feature)

**1.3.1** The system SHALL reliably detect persons using YOLO "person" class.

**1.3.2** The system SHALL trigger person alerts when confidence >= 0.7.

**1.3.3** The system SHALL require person detection in at least 3 consecutive frames before confirming alert.

**1.3.4** The system SHALL create PersonEvent with confidence, timestamp, and bounding box.

**1.3.5** The system SHALL assign "medium" risk level to person detections.

### 1.4 Simulated Weapon Detection (Demo Feature)

**1.4.1** The system MAY simulate weapon detection for demonstration purposes.

**1.4.2** IF simulated, the system SHALL randomly classify 10% of person detections as "weapon" events.

**1.4.3** Simulated weapon events SHALL alternate between "knife" and "gun" types.

**1.4.4** The system SHALL assign "critical" risk level to simulated gun detections.

**1.4.5** The system SHALL assign "high" risk level to simulated knife detections.

**1.4.6** The system SHALL clearly document that weapon detection is simulated in README.

### 1.5 Multi-frame Confirmation

**1.5.1** The system SHALL maintain separate counters for each event type.

**1.5.2** The system SHALL increment counter by 1 when event is detected in a frame.

**1.5.3** The system SHALL reset counter to 0 when event is NOT detected in a frame.

**1.5.4** The system SHALL confirm alert when counter reaches the configured threshold for that event type.

**1.5.5** The system SHALL reset counter to 0 after alert is confirmed and created.

**1.5.6** The system SHALL trigger alert exactly once per continuous event sequence.

### 1.6 Alert Creation and Storage

**1.6.1** The system SHALL capture the incident frame when alert is confirmed.

**1.6.2** The system SHALL encode incident frame to JPEG format with quality=85.

**1.6.3** The system SHALL upload incident image to Appwrite Storage bucket.

**1.6.4** The system SHALL create alert document in Appwrite Database with the following fields:
- event_type (string)
- risk_level (string)
- camera_id (string)
- timestamp (ISO 8601 string)
- image_url (string)
- confidence (float)
- metadata (JSON object)

**1.6.5** The system SHALL generate unique filename for each incident image using event type and timestamp.

**1.6.6** The system SHALL store image URL from Appwrite Storage in alert document.

**1.6.7** The system SHALL trigger Appwrite realtime notification when alert document is created.

### 1.7 Professional HUD Dashboard

**1.7.1** The system SHALL provide a professional HUD interface with cyberpunk/tech aesthetic.

**1.7.2** The dashboard SHALL display real-time video feed with detection overlays and bounding boxes.

**1.7.3** The dashboard SHALL show animated threat indicators with color-coded glowing effects.

**1.7.4** The dashboard SHALL display live statistics panel with:
- Total threats detected (by type)
- System uptime in seconds
- Current FPS
- Active camera count

**1.7.5** The dashboard SHALL use color-coded threat levels with glowing effects:
- CRITICAL (red glow) for gun weapons
- HIGH (orange glow) for knife weapons
- MEDIUM (yellow glow) for person detections

**1.7.6** The dashboard SHALL use dark theme with neon accents (cyan #00ffff, magenta #ff00ff, yellow #ffff00).

**1.7.7** The dashboard SHALL implement smooth CSS animations and transitions for new alerts.

**1.7.8** The dashboard SHALL use professional typography (monospace for data, sans-serif for labels).

**1.7.9** The dashboard SHALL display alert timeline with scrollable history.

**1.7.10** The dashboard SHALL show pulsing threat indicators for active alerts.

**1.7.11** The dashboard SHALL display a scrollable list of alerts ordered by timestamp (newest first).

**1.7.12** The dashboard SHALL display alert cards with event type, risk level badge, timestamp, and thumbnail image.

**1.7.13** The dashboard SHALL subscribe to Appwrite realtime channel for live alert updates.

**1.7.14** The dashboard SHALL automatically display new alerts when realtime notification is received.

**1.7.15** The dashboard SHALL allow clicking on alert to view full incident image in modal.

**1.7.16** The dashboard SHALL display system status indicator (running/stopped).

**1.7.17** The dashboard SHALL fetch incident images from Appwrite Storage using image URLs.

**1.7.18** The dashboard SHALL update statistics panel every 5 seconds.

### 1.8 SMS Alert System (Optional)

**1.8.1** The system MAY send emergency SMS notifications for critical and high-risk alerts.

**1.8.2** IF enabled, the system SHALL use Appwrite Messaging service with Twilio integration for SMS delivery.

**1.8.3** The system SHALL format SMS messages as: "[CYPHER ALERT] {event_type} detected at {camera_id} - {timestamp} Risk: {risk_level}"

**1.8.4** The system SHALL support configurable recipient phone numbers in E.164 format.

**1.8.5** The system SHALL implement rate limiting of maximum 5 SMS per hour per recipient.

**1.8.6** The system SHALL track SMS sent count and reset counter every hour.

**1.8.7** The system SHALL log rate limit violations with event type and timestamp.

**1.8.8** The system SHALL only send SMS for alerts with risk level >= configured threshold (default: high).

**1.8.9** The system SHALL allow enabling/disabling SMS alerts via configuration.

### 1.9 Modular Architecture

**1.9.1** The system SHALL organize code into modular packages:
- cypher.detection - All detection logic
- cypher.alerts - Alert management (SMS, database)
- cypher.vision - Video processing and frame capture
- cypher.api - FastAPI endpoints
- cypher.config - Configuration management
- cypher.utils - Shared utilities

**1.9.2** Each module SHALL have clear interfaces and minimal dependencies.

**1.9.3** The system SHALL use dependency injection for component initialization.

**1.9.4** The system SHALL provide structured logging with JSON output.

**1.9.5** All modules SHALL include __init__.py with public API exports.

**1.9.6** The system SHALL use type hints for all function parameters and return values.

**1.9.7** The system SHALL use dataclasses for all configuration and data models.

### 1.10 Alert Manager

**1.10.1** The system SHALL provide centralized AlertManager to coordinate all alert systems.

**1.10.2** The AlertManager SHALL process confirmed events and trigger:
- Incident frame upload to storage
- Alert document creation in database
- SMS alert (if risk level and rate limit conditions met)
- Realtime notification (automatic via Appwrite)

**1.10.3** The AlertManager SHALL calculate and track alert statistics.

**1.10.4** The AlertManager SHALL enforce global rate limiting (max 10 alerts per minute).

**1.10.5** The AlertManager SHALL provide unified interface for alert processing.

### 1.11 REST API Endpoints

**1.11.1** The system SHALL provide POST /api/start endpoint to start surveillance on a video source.

**1.11.2** The system SHALL provide POST /api/stop endpoint to stop active surveillance.

**1.11.3** The system SHALL provide GET /api/alerts endpoint to retrieve recent alerts (default limit: 50).

**1.11.4** The system SHALL provide GET /api/status endpoint to get surveillance system status.

**1.11.5** The system SHALL return JSON responses for all API endpoints.

**1.11.6** The system SHALL handle CORS to allow frontend dashboard access.

**1.11.7** The system SHALL provide GET /api/statistics endpoint to retrieve HUD statistics.

**1.11.8** The system SHALL provide POST /api/sms/settings endpoint to update SMS configuration (if SMS enabled).

**1.11.9** The system SHALL provide GET /api/sms/history endpoint to retrieve SMS delivery history (if SMS enabled).

### 1.12 Authentication and Authorization (Added for Security)

**1.12.1** The system SHALL implement API key authentication for all API endpoints.

**1.12.2** The system SHALL validate API keys before processing requests.

**1.12.3** The system SHALL return HTTP 401 for unauthorized requests.

**1.12.4** The system SHALL store API keys in environment variables.

**1.12.5** The system SHALL support multiple API keys for different clients.

### 1.13 Offline Mode (Added for Reliability)

**1.13.1** The system SHALL queue alerts locally if Appwrite connection is unavailable.

**1.13.2** The system SHALL retry uploading queued alerts when connection is restored.

**1.13.3** The system SHALL store queued alerts in local JSON file.

**1.13.4** The system SHALL limit queue size to 100 alerts maximum.

**1.13.5** The system SHALL log connection failures with timestamps.

---

## 2. Non-Functional Requirements

### 2.1 Performance

**2.1.1** The system SHALL process at least 10 frames per second on standard laptop hardware (CPU-only).

**2.1.2** The system SHALL complete alert creation (including image upload) within 500ms.

**2.1.3** The system SHALL keep memory usage under 2GB during operation.

**2.1.4** The system SHALL deliver realtime notifications to dashboard within 2 seconds of alert creation.

**2.1.5** The system SHALL implement automatic memory cleanup for processed frames.

### 2.2 Reliability

**2.2.1** The system SHALL continue processing subsequent frames if a single frame processing fails.

**2.2.2** The system SHALL stop surveillance if more than 10 consecutive frame processing errors occur.

**2.2.3** The system SHALL retry Appwrite API calls up to 3 times with exponential backoff on failure.

**2.2.4** The system SHALL queue alerts locally if Appwrite connection is unavailable.

**2.2.5** The system SHALL properly release video capture resources on shutdown.

**2.2.6** The system SHALL implement graceful shutdown on SIGINT/SIGTERM signals.

**2.2.7** The system SHALL log all errors with stack traces for debugging.

### 2.3 Usability

**2.3.1** The system SHALL provide clear error messages for common setup issues (missing model, invalid credentials).

**2.3.2** The system SHALL include README with setup instructions and configuration examples.

**2.3.3** The dashboard SHALL use color-coded risk level badges (critical=red, high=orange, medium=yellow).

**2.3.4** The system SHALL log processing status and errors to console for debugging.

**2.3.5** The system SHALL provide example .env file with all required variables.

### 2.4 Security

**2.4.1** The system SHALL store Appwrite credentials in environment variables, not in code.

**2.4.2** The system SHALL never commit credentials to version control (.env in .gitignore).

**2.4.3** The system SHALL use Appwrite private storage buckets for incident images.

**2.4.4** The system SHALL validate all event data before creating alerts.

**2.4.5** The system SHALL implement rate limiting (max 10 alerts per minute) to prevent spam.

**2.4.6** The system SHALL configure CORS to allow only dashboard origin.

**2.4.7** The system SHALL not log sensitive data (API keys, video frames) in logs.

**2.4.8** The system SHALL implement API key authentication for all endpoints.

**2.4.9** The system SHALL sanitize all user inputs to prevent injection attacks.

### 2.5 Maintainability

**2.5.1** The system SHALL use Pydantic models for all data structures with validation.

**2.5.2** The system SHALL organize code into modular components (detector, event_engine, appwrite_client, main_api).

**2.5.3** The system SHALL include docstrings for all public functions and classes.

**2.5.4** The system SHALL use type hints for function parameters and return values.

**2.5.5** The system SHALL pin dependency versions in requirements.txt.

**2.5.6** The system SHALL follow PEP 8 style guidelines.

**2.5.7** The system SHALL use meaningful variable and function names.

### 2.6 Testability

**2.6.1** The system SHALL achieve at least 70% code coverage for core detection and confirmation logic.

**2.6.2** The system SHALL provide unit tests for all detection functions.

**2.6.3** The system SHALL provide integration tests with mock Appwrite instance.

**2.6.4** The system SHALL use pytest as the testing framework.

**2.6.5** The system SHALL provide test fixtures for common test scenarios.

### 2.7 Compatibility

**2.7.1** The system SHALL support Python 3.9 or higher.

**2.7.2** The system SHALL work on Windows, macOS, and Linux operating systems.

**2.7.3** The dashboard SHALL work on modern web browsers (Chrome, Firefox, Safari, Edge).

**2.7.4** The system SHALL support video formats compatible with OpenCV (MP4, AVI, MOV).

**2.7.5** The system SHALL support both webcam and video file inputs.

### 2.8 Scalability Constraints (Acknowledged for Hackathon)

**2.8.1** The system SHALL process only one video source at a time (single-threaded).

**2.8.2** The system SHALL use CPU-only inference (no GPU acceleration required).

**2.8.3** The system SHALL not implement distributed processing or load balancing.

**2.8.4** The system SHALL not implement video buffering or queue management.

**2.8.5** The system SHALL document scalability limitations in README.

---

## 3. Data Requirements

### 3.1 Appwrite Database Schema

**3.1.1** The system SHALL use database name "surveillance".

**3.1.2** The system SHALL use collection name "alerts".

**3.1.3** The alerts collection SHALL have the following attributes:
- event_type: string (required, max 50 chars)
- risk_level: string (required, max 20 chars)
- camera_id: string (required, max 50 chars)
- timestamp: string (required, ISO 8601 format)
- image_url: string (required, max 500 chars)
- confidence: float (required, 0.0 to 1.0)
- metadata: string (required, JSON serialized, max 1000 chars)

**3.1.4** The system SHALL use storage bucket name "incidents" for incident images.

**3.1.5** The system SHALL implement automatic cleanup of alerts older than 7 days.

### 3.2 Configuration Data

**3.2.1** The system SHALL support the following configurable parameters:
- person_confidence_threshold (default: 0.7)
- person_frame_threshold (default: 3)
- weapon_simulation_enabled (default: false)
- weapon_simulation_rate (default: 0.1)

**3.2.2** The system SHALL load configuration from environment variables or config file.

**3.2.3** The system SHALL support SMS alert configuration (if enabled):
- sms_enabled (default: false)
- sms_recipients (list of phone numbers)
- sms_min_risk_level (default: "high")
- sms_rate_limit_per_hour (default: 5)
- sms_twilio_provider_id (Appwrite Messaging provider ID)

**3.2.4** The system SHALL validate all configuration values on startup.

### 3.3 Model Data

**3.3.1** The system SHALL use YOLOv8n model file (yolov8n.pt).

**3.3.2** The system SHALL automatically download YOLOv8n model on first run if not present.

**3.3.3** The system SHALL store model file in models/ directory.

**3.3.4** The system SHALL verify model file integrity before loading.

---

## 4. Interface Requirements

### 4.1 External Service Interfaces

**4.1.1** The system SHALL integrate with Appwrite Cloud API v1.

**4.1.2** The system SHALL use Appwrite Python SDK v4.1.0 or compatible.

**4.1.3** The system SHALL use Appwrite Web SDK v13.0.0 or compatible for frontend.

**4.1.4** The system SHALL handle Appwrite API rate limits gracefully.

### 4.2 Video Input Interfaces

**4.2.1** The system SHALL accept video file paths as input.

**4.2.2** The system SHALL accept webcam device IDs (0, 1, 2, etc.) as input.

**4.2.3** The system SHALL accept RTSP stream URLs as input.

**4.2.4** The system SHALL validate video source before starting surveillance.

### 4.3 API Response Formats

**4.3.1** POST /api/start SHALL return:
```json
{
  "status": "started",
  "video_source": "string",
  "camera_id": "string",
  "timestamp": "ISO 8601 string"
}
```

**4.3.2** POST /api/stop SHALL return:
```json
{
  "status": "stopped",
  "frames_processed": "integer",
  "alerts_created": "integer",
  "uptime_seconds": "float"
}
```

**4.3.3** GET /api/alerts SHALL return:
```json
{
  "alerts": [
    {
      "id": "string",
      "event_type": "string",
      "risk_level": "string",
      "camera_id": "string",
      "timestamp": "string",
      "image_url": "string",
      "confidence": "float",
      "metadata": "object"
    }
  ],
  "total": "integer"
}
```

**4.3.4** GET /api/status SHALL return:
```json
{
  "status": "running|stopped",
  "video_source": "string",
  "frames_processed": "integer",
  "alerts_created": "integer",
  "uptime_seconds": "float",
  "current_fps": "float",
  "memory_usage_mb": "float"
}
```

**4.3.5** GET /api/statistics SHALL return:
```json
{
  "total_threats": "integer",
  "threats_by_type": {
    "person": "integer",
    "weapon": "integer"
  },
  "system_uptime_seconds": "float",
  "current_fps": "float",
  "active_cameras": "integer",
  "last_alert_timestamp": "string|null",
  "alerts_last_hour": "integer"
}
```

---

## 5. Constraints

### 5.1 Technical Constraints

**5.1.1** The system SHALL use Python as the primary programming language.

**5.1.2** The system SHALL use FastAPI as the web framework.

**5.1.3** The system SHALL use OpenCV for video processing.

**5.1.4** The system SHALL use Ultralytics YOLOv8 for object detection.

**5.1.5** The system SHALL use Appwrite for backend services (database, storage, realtime).

**5.1.6** The frontend SHALL use vanilla JavaScript (no heavy frameworks like React/Vue).

### 5.2 Resource Constraints

**5.2.1** The system SHALL run on standard laptop hardware (no GPU required).

**5.2.2** The system SHALL use less than 2GB of RAM during operation.

**5.2.3** The system SHALL use less than 2GB of disk space for models and dependencies.

**5.2.4** The system SHALL implement memory cleanup to prevent leaks.

### 5.3 Time Constraints

**5.3.1** The system SHALL be suitable for hackathon demonstration (not production-scale).

**5.3.2** The system SHALL prioritize demo-readiness over production features.

**5.3.3** The system SHALL focus on core functionality over advanced features.

**5.3.4** The system SHALL be implementable within 8-12 hours of development time.

---

## 6. Acceptance Criteria

### 6.1 Person Detection Acceptance

**6.1.1** GIVEN a video with a person visible for 3+ consecutive frames at confidence >= 0.7, WHEN the system processes the video, THEN a person alert with risk_level="medium" SHALL be created.

**6.1.2** GIVEN a video with a person visible for only 2 frames, WHEN the system processes the video, THEN no person alert SHALL be created.

### 6.2 Simulated Weapon Detection Acceptance (If Enabled)

**6.2.1** GIVEN weapon simulation is enabled, WHEN the system detects persons, THEN approximately 10% SHALL be classified as weapon events.

**6.2.2** GIVEN a simulated weapon event, WHEN the event is created, THEN it SHALL have either "knife" or "gun" as weapon_type.

### 6.3 Alert Storage Acceptance

**6.3.1** GIVEN an alert is confirmed, WHEN the system creates the alert, THEN the incident image SHALL be uploaded to Appwrite Storage AND the alert document SHALL be created in Appwrite Database with valid image_url.

### 6.4 Dashboard Acceptance

**6.4.1** GIVEN the dashboard is open and subscribed to realtime, WHEN an alert is created, THEN the alert SHALL appear in the dashboard within 2 seconds.

**6.4.2** GIVEN the dashboard displays an alert, WHEN the user clicks on the alert, THEN the full incident image SHALL be displayed in a modal.

### 6.5 Performance Acceptance

**6.5.1** GIVEN a video source, WHEN the system processes frames, THEN the average processing rate SHALL be at least 10 FPS.

**6.5.2** GIVEN an alert is confirmed, WHEN the system creates the alert, THEN the total time (including image upload) SHALL be less than 500ms.

### 6.6 Error Handling Acceptance

**6.6.1** GIVEN Appwrite connection fails, WHEN the system attempts to create an alert, THEN the system SHALL queue the alert locally and retry later.

**6.6.2** GIVEN a frame processing error occurs, WHEN the system encounters the error, THEN the system SHALL log the error and continue processing the next frame.

### 6.7 Security Acceptance

**6.7.1** GIVEN an API request without valid API key, WHEN the request is received, THEN the system SHALL return HTTP 401 Unauthorized.

**6.7.2** GIVEN credentials in .env file, WHEN the repository is committed, THEN .env SHALL NOT be included in version control.

---

## 7. Known Limitations and Workarounds

### 7.1 YOLO Weapon Detection Limitation

**Limitation:** YOLOv8n with COCO dataset does not include "knife" or "gun" classes.

**Workarounds:**
1. Train custom YOLOv8 model with weapon dataset (time-intensive)
2. Use weapon simulation for demo purposes (recommended for hackathon)
3. Use pre-trained weapon detection model from Roboflow or similar

**Recommendation:** Use weapon simulation for hackathon demo, document limitation clearly.

### 7.2 Single Camera Limitation

**Limitation:** System processes only one video source at a time.

**Workarounds:**
1. Run multiple instances of the system (one per camera)
2. Implement multi-threading (requires significant refactoring)

**Recommendation:** Accept limitation for hackathon, document in README.

### 7.3 Appwrite Dependency

**Limitation:** System requires internet connection for Appwrite services.

**Workarounds:**
1. Implement local queue for offline operation
2. Use local SQLite database as fallback

**Recommendation:** Implement local queue (already in requirements 1.13).

---

## Document Metadata

**Version:** 2.0 (Cleaned and Consolidated)
**Last Updated:** 2024
**Status:** Final
**Author:** Kiro AI Assistant
**Changes from v1.0:**
- Fixed duplicate section numbering
- Removed unrealistic fight/running/accident detection
- Added YOLO weapon detection limitation
- Added authentication requirements
- Added offline mode requirements
- Simplified to focus on person detection + simulated weapons
- Added known limitations section
- Improved acceptance criteria
- Added security requirements
