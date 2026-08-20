import fitz
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def make_pdf() -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "Vector PDF Suite")
    content = document.tobytes()
    document.close()
    return content


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_rejects_non_pdf() -> None:
    response = client.post("/api/convert/pdf-to-images", files={"file": ("bad.txt", b"hello", "text/plain")})
    assert response.status_code == 415


def test_conversion_is_queued() -> None:
    response = client.post("/api/convert/pdf-to-images", files={"file": ("sample.pdf", make_pdf(), "application/pdf")})
    assert response.status_code == 202
    assert response.json()["job_id"]

