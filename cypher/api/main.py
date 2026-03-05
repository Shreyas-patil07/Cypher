"""FastAPI app providing control and HUD endpoints."""

from __future__ import annotations

import logging
from pathlib import Path
import threading
import time
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from cypher.surveillance import SurveillanceSystem
from cypher.alerts import (
    AlertManager,
    AppwriteAlertRepository,
    AppwriteSMSClient,
    AppwriteStorageAdapter,
    NoopRealtimePublisher,
    RiskLevel,
    SMSAgent,
    SMSAgentConfig,
)
from cypher.config import Settings, get_settings

LOG = logging.getLogger(__name__)

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"


def _try_build_appwrite_client(settings: Settings):
    """Build Appwrite client if credentials exist, otherwise return None."""
    if not settings.appwrite_project_id or not settings.appwrite_api_key:
        LOG.warning("Appwrite credentials not configured — running in demo mode")
        return None
    from cypher.utils import AppwriteClient

    return AppwriteClient(
        endpoint=settings.appwrite_endpoint,
        project_id=settings.appwrite_project_id,
        api_key=settings.appwrite_api_key,
        database_id=settings.appwrite_database_id,
        alerts_collection_id=settings.appwrite_alerts_collection_id,
        storage_bucket_id=settings.appwrite_storage_bucket_id,
    )


def build_sms_agent(settings: Settings) -> SMSAgent:
    sms_client = AppwriteSMSClient(
        endpoint=settings.appwrite_endpoint,
        project_id=settings.appwrite_project_id,
        api_key=settings.appwrite_api_key,
    )
    cfg = SMSAgentConfig(
        enabled=settings.alert_sms_enabled,
        recipients=settings.alert_sms_recipients,
        min_risk_level=RiskLevel(settings.alert_sms_min_risk),
        rate_limit_per_hour=max(settings.alert_sms_rate_limit_min, 0),
    )
    return SMSAgent(config=cfg, messaging_client=sms_client)


def _build_alert_manager(settings: Settings, appwrite_client) -> AlertManager:
    """Build AlertManager with or without Appwrite backends."""
    storage = AppwriteStorageAdapter(appwrite_client) if appwrite_client else None
    repository = AppwriteAlertRepository(appwrite_client) if appwrite_client else None
    sms_agent = build_sms_agent(settings) if appwrite_client and settings.alert_sms_enabled else None
    return AlertManager(
        storage_client=storage,
        alert_repository=repository,
        realtime_publisher=NoopRealtimePublisher(),
        sms_agent=sms_agent,
    )


class SurveillanceController:
    """Manages lifecycle of the surveillance thread."""

    def __init__(self, system: SurveillanceSystem) -> None:
        self.system = system
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._running = False

    def start(self) -> None:
        with self._lock:
            if self._running:
                raise RuntimeError("Surveillance already running")
            self._running = True
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        with self._lock:
            if not self._running:
                return
            self.system.stop()
            self._running = False

    def _run(self) -> None:
        try:
            self.system.start()
        finally:
            self._running = False

    @property
    def running(self) -> bool:
        return self._running


# ---------------------------------------------------------------------------
# Instantiate core services (tolerating missing Appwrite creds)
# ---------------------------------------------------------------------------
_settings = get_settings()
_appwrite_client = _try_build_appwrite_client(_settings)
_alert_manager = _build_alert_manager(_settings, _appwrite_client)
_surveillance_system = SurveillanceSystem(settings=_settings, alert_manager=_alert_manager)
_controller = SurveillanceController(_surveillance_system)

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(title="CYPHER API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Simple API key auth (optional)
def require_api_key(x_api_key: str | None = Header(default=None), settings: Settings = Depends(get_settings)):
    expected = settings.dashboard_api_key
    if expected and x_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return True


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class StartRequest(BaseModel):
    video_source: str | int | None = None


class StatusResponse(BaseModel):
    status: str
    video_source: str | int | None
    running: bool
    frames_processed: int = 0
    alerts_created: int = 0
    uptime_seconds: float = 0.0
    current_fps: float = 0.0


class AlertItem(BaseModel):
    id: str
    event_type: str
    risk_level: str
    camera_id: str
    timestamp: str
    image_url: str | None
    confidence: float
    metadata: dict


class AlertsResponse(BaseModel):
    alerts: list[AlertItem]
    total: int


class StatisticsResponse(BaseModel):
    total_threats: int
    threats_by_type: dict
    system_uptime_seconds: float
    current_fps: float
    active_cameras: int
    last_alert_timestamp: str | None
    alerts_last_hour: int = 0


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------
@app.post("/api/start", dependencies=[Depends(require_api_key)])
def start_surveillance(payload: StartRequest):
    if payload.video_source is not None:
        _surveillance_system.capture = _surveillance_system.capture.__class__(payload.video_source)
    try:
        _controller.start()
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"status": "started", "video_source": payload.video_source or _settings.video_source}


@app.post("/api/stop", dependencies=[Depends(require_api_key)])
def stop_surveillance():
    _controller.stop()
    return {"status": "stopped"}


@app.get("/api/status", response_model=StatusResponse)
def get_status():
    snap = _surveillance_system.stats.snapshot()
    return StatusResponse(
        status="running" if _controller.running else "stopped",
        video_source=_settings.video_source,
        running=_controller.running,
        frames_processed=snap["frames_processed"],
        alerts_created=snap["alerts_created"],
        uptime_seconds=snap["system_uptime_seconds"],
        current_fps=snap["current_fps"],
    )


@app.get("/api/alerts", response_model=AlertsResponse)
def list_alerts(limit: int = 50):
    if _appwrite_client is None:
        return AlertsResponse(alerts=[], total=0)
    docs = _appwrite_client.get_alerts(limit=limit)
    alerts = [
        AlertItem(
            id=doc.get("$id", ""),
            event_type=doc.get("event_type", ""),
            risk_level=doc.get("risk_level", ""),
            camera_id=doc.get("camera_id", ""),
            timestamp=doc.get("timestamp", ""),
            image_url=doc.get("image_url") or None,
            confidence=float(doc.get("confidence", 0.0)),
            metadata=doc.get("metadata") or {},
        )
        for doc in docs
    ]
    return AlertsResponse(alerts=alerts, total=len(alerts))


@app.get("/api/statistics", response_model=StatisticsResponse)
def get_statistics():
    snap = _surveillance_system.stats.snapshot()
    return StatisticsResponse(
        total_threats=snap["total_threats"],
        threats_by_type=snap["threats_by_type"],
        system_uptime_seconds=snap["system_uptime_seconds"],
        current_fps=snap["current_fps"],
        active_cameras=snap["active_cameras"],
        last_alert_timestamp=snap["last_alert_timestamp"],
    )


# ---------------------------------------------------------------------------
# Serve frontend
# ---------------------------------------------------------------------------
@app.get("/")
def serve_dashboard():
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"detail": "Frontend not found"}


if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")
