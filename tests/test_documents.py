"""Documents: initiate and complete (S3 mocked)."""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


@patch("app.api.documents.s3_client")
def test_documents_initiate(mock_s3, client: TestClient, auth_headers):
    mock_s3.generate_presigned_url.return_value = "https://s3.example.com/presigned"
    cr = client.post(
        "/api/applicants/",
        headers=auth_headers,
        json={"first_name": "D", "last_name": "Doc", "latest_education": "BS"},
    )
    bundle_id = cr.json()["bundle_id"]
    r = client.post(
        f"/api/bundles/{bundle_id}/documents/initiate?filename=transcript.pdf&content_type=application/pdf",
        headers=auth_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert "upload_url" in data
    assert data["document_id"] > 0
    assert "key" in data


@patch("app.api.documents.s3_client")
def test_documents_initiate_bundle_404(mock_s3, client: TestClient, auth_headers):
    r = client.post(
        "/api/bundles/99999/documents/initiate?filename=x.pdf&content_type=application/pdf",
        headers=auth_headers,
    )
    assert r.status_code == 404


@patch("app.api.documents.s3_client")
def test_documents_complete(mock_s3, client: TestClient, auth_headers):
    mock_s3.generate_presigned_url.return_value = "https://s3.example.com/presigned"
    cr = client.post(
        "/api/applicants/",
        headers=auth_headers,
        json={"first_name": "D2", "last_name": "Doc2", "latest_education": "MS"},
    )
    bundle_id = cr.json()["bundle_id"]
    init_r = client.post(
        f"/api/bundles/{bundle_id}/documents/initiate?filename=degree.pdf&content_type=application/pdf",
        headers=auth_headers,
    )
    doc_id = init_r.json()["document_id"]
    key = init_r.json()["key"]
    mock_s3.head_object.return_value = {"ContentLength": 2048}
    r = client.post(
        f"/api/documents/{doc_id}/complete",
        headers=auth_headers,
        json={"key": key},
    )
    assert r.status_code == 200
    assert r.json().get("status") == "ok"
