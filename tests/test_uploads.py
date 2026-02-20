"""Uploads: initiate and complete (S3 mocked)."""
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


@patch("app.api.uploads.s3_client")
def test_uploads_initiate(mock_s3, client: TestClient, auth_headers):
    mock_s3.generate_presigned_url.return_value = "https://s3.example.com/presigned"
    r = client.post(
        "/api/uploads/initiate?content_type=application/pdf",
        headers=auth_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert "upload_url" in data
    assert data["content_type"] == "application/pdf"
    assert "key" in data


@patch("app.api.uploads.s3_client")
def test_uploads_complete(mock_s3, client: TestClient, auth_headers):
    mock_s3.generate_presigned_url.return_value = "https://s3.example.com/presigned"
    init_r = client.post(
        "/api/uploads/initiate?content_type=application/pdf",
        headers=auth_headers,
    )
    key = init_r.json()["key"]
    mock_s3.head_object.return_value = {"ContentLength": 1024}
    r = client.post(
        "/api/uploads/complete",
        params={"key": key},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json().get("status") in ("received", "ok") or "key" in r.json()


@patch("app.api.uploads.s3_client")
def test_uploads_complete_not_found(mock_s3, client: TestClient, auth_headers):
    from botocore.exceptions import ClientError
    err = ClientError({"Error": {"Code": "404"}}, "HeadObject")
    err.response = {"ResponseMetadata": {"HTTPStatusCode": 404}}
    mock_s3.head_object.side_effect = err
    r = client.post(
        "/api/uploads/complete",
        params={"key": "uploads/1/nonexistent"},
        headers=auth_headers,
    )
    assert r.status_code == 400
