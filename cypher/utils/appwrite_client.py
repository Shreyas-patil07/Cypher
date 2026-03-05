"""Thin wrapper around Appwrite SDK for storage and database operations."""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional

from appwrite.client import Client
from appwrite.exception import AppwriteException
from appwrite.services.databases import Databases
from appwrite.services.storage import Storage

from cypher.alerts import AlertDocument


class AppwriteClient:
    """Provides upload and alert document helpers with basic retry logic."""

    def __init__(
        self,
        *,
        endpoint: str,
        project_id: str,
        api_key: str,
        database_id: str,
        alerts_collection_id: str,
        storage_bucket_id: str,
        max_retries: int = 3,
        backoff_seconds: float = 0.5,
    ) -> None:
        self.database_id = database_id
        self.alerts_collection_id = alerts_collection_id
        self.storage_bucket_id = storage_bucket_id
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds

        self.client = Client()
        self.client.set_endpoint(endpoint)
        self.client.set_project(project_id)
        self.client.set_key(api_key)
        self.databases = Databases(self.client)
        self.storage = Storage(self.client)

    # Storage -----------------------------------------------------------------
    def upload_image(self, *, filename: str, data: bytes, content_type: str) -> str:
        payload = {
            "file": (filename, data, content_type),
        }
        response = self._with_retries(lambda: self.storage.create_file(self.storage_bucket_id, "unique()", payload))
        return response.get("$id", "")

    # Database ----------------------------------------------------------------
    def create_alert(self, document: AlertDocument) -> str:
        payload = {
            "event_type": document.event_type,
            "risk_level": document.risk_level,
            "camera_id": document.camera_id,
            "timestamp": document.timestamp.isoformat(),
            "image_url": document.image_url or "",
            "confidence": document.confidence,
            "metadata": json.dumps(document.metadata),
        }
        response = self._with_retries(
            lambda: self.databases.create_document(
                self.database_id, self.alerts_collection_id, "unique()", payload
            )
        )
        return response.get("$id", "")

    def get_alerts(self, *, limit: int = 50) -> List[Dict[str, Any]]:
        response = self._with_retries(
            lambda: self.databases.list_documents(
                self.database_id,
                self.alerts_collection_id,
                queries=["limit({})".format(limit), "orderDesc($createdAt)"],
            )
        )
        return response.get("documents", [])

    # Health ------------------------------------------------------------------
    def health_check(self) -> bool:
        try:
            self.get_alerts(limit=1)
            return True
        except AppwriteException:
            return False

    # Retry wrapper -----------------------------------------------------------
    def _with_retries(self, fn):
        last_exc: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return fn()
            except AppwriteException as exc:  # pragma: no cover - external service
                last_exc = exc
                if attempt >= self.max_retries:
                    raise
                time.sleep(self.backoff_seconds * attempt)
        if last_exc:
            raise last_exc
        raise RuntimeError("Unknown error in Appwrite client")
