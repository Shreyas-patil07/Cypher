"""Central application settings using Pydantic BaseSettings."""

from __future__ import annotations

from typing import List, Optional, Sequence

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    # Appwrite
    appwrite_endpoint: str = Field("https://cloud.appwrite.io/v1", alias="APPWRITE_ENDPOINT")
    appwrite_project_id: str = Field("", alias="APPWRITE_PROJECT_ID")
    appwrite_api_key: str = Field("", alias="APPWRITE_API_KEY")
    appwrite_database_id: str = Field("surveillance", alias="APPWRITE_DATABASE_ID")
    appwrite_alerts_collection_id: str = Field("alerts", alias="APPWRITE_ALERTS_COLLECTION_ID")
    appwrite_storage_bucket_id: str = Field("incidents", alias="APPWRITE_STORAGE_BUCKET_ID")
    appwrite_realtime_channel: str = Field("alerts", alias="APPWRITE_REALTIME_CHANNEL")

    # Video / detection
    video_source: str | int = Field("0", alias="VIDEO_SOURCE")
    frame_skip: int = Field(1, alias="FRAME_SKIP", ge=0)
    frame_size: int = Field(640, alias="FRAME_SIZE", ge=64)
    person_confidence_threshold: float = Field(0.7, alias="PERSON_CONFIDENCE_THRESHOLD", ge=0.0, le=1.0)
    person_confirmation_frames: int = Field(3, alias="PERSON_CONFIRMATION_FRAMES", ge=1)
    weapon_simulation_enabled: bool = Field(True, alias="WEAPON_SIMULATION_ENABLED")
    weapon_simulation_rate: float = Field(0.1, alias="WEAPON_SIMULATION_RATE", ge=0.0, le=1.0)

    # Alerting
    alert_image_quality: int = Field(85, alias="ALERT_IMAGE_QUALITY", ge=1, le=100)
    alert_dispatch_enabled: bool = Field(True, alias="ALERT_DISPATCH_ENABLED")
    alert_email_sender: str = Field("alerts@cypher.local", alias="ALERT_EMAIL_SENDER")
    alert_email_recipients: List[str] = Field(default_factory=list, alias="ALERT_EMAIL_RECIPIENTS")

    # SMS
    alert_sms_enabled: bool = Field(False, alias="ALERT_SMS_ENABLED")
    alert_sms_recipients: List[str] = Field(default_factory=list, alias="ALERT_SMS_RECIPIENTS")
    alert_sms_min_risk: str = Field("high", alias="ALERT_SMS_MIN_RISK")
    alert_sms_rate_limit_min: int = Field(2, alias="ALERT_SMS_RATE_LIMIT_MIN", ge=0)

    # Intelligence layer
    default_camera_lat: Optional[float] = Field(None, alias="DEFAULT_CAMERA_LAT")
    default_camera_lon: Optional[float] = Field(None, alias="DEFAULT_CAMERA_LON")
    max_authority_distance_km: float = Field(25.0, alias="MAX_AUTHORITY_DISTANCE_KM", ge=0)

    # SMTP (optional)
    smtp_host: Optional[str] = Field(None, alias="SMTP_HOST")
    smtp_port: int = Field(587, alias="SMTP_PORT")
    smtp_username: Optional[str] = Field(None, alias="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(None, alias="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(True, alias="SMTP_USE_TLS")

    # API
    api_host: str = Field("0.0.0.0", alias="API_HOST")
    api_port: int = Field(8000, alias="API_PORT")
    dashboard_api_key: Optional[str] = Field(None, alias="DASHBOARD_API_KEY")

    @field_validator("video_source", mode="before")
    @classmethod
    def _coerce_video_source(cls, v):
        # Convert numeric strings to int for OpenCV camera index convenience.
        if isinstance(v, str) and v.isdigit():
            return int(v)
        return v

    @field_validator("alert_email_recipients", "alert_sms_recipients", mode="before")
    @classmethod
    def _split_recipients(cls, v):
        if v is None or v == "":
            return []
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return list(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        populate_by_name=True,
    )


def get_settings() -> Settings:
    """Factory helper for dependency injection."""

    return Settings()
