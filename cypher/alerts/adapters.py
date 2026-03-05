"""Adapters to bridge AppwriteClient into AlertManager protocols."""

from __future__ import annotations

from typing import Any

from cypher.utils import AppwriteClient

from .alert_manager import AlertDocument, AlertRepository, IncidentStorageClient, RealtimePublisher


class AppwriteStorageAdapter(IncidentStorageClient):
    def __init__(self, client: AppwriteClient) -> None:
        self.client = client

    def upload(self, *, filename: str, data: bytes, content_type: str) -> str:
        file_id = self.client.upload_image(filename=filename, data=data, content_type=content_type)
        # Appwrite file view URL pattern; adjust permissions as needed.
        return f"/storage/buckets/{self.client.storage_bucket_id}/files/{file_id}/view"


class AppwriteAlertRepository(AlertRepository):
    def __init__(self, client: AppwriteClient) -> None:
        self.client = client

    def create(self, document: AlertDocument) -> str:
        return self.client.create_alert(document)


class NoopRealtimePublisher(RealtimePublisher):
    def publish(self, document: AlertDocument) -> None:  # pragma: no cover - noop
        return None
