import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search_bm25_returns_relevant_results(client):
    response = client.get(
        "/api/search", params={"q": "sepatu lari ringan", "mode": "bm25", "top_k": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "bm25"
    assert data["total_results"] > 0
    assert data["results"][0]["product"] is not None


def test_search_semantic_returns_503_when_disabled(client):
    """Memverifikasi graceful degradation (Bagian 9.9): kalau semantic
    search dimatikan, endpoint tidak crash -- ia mengembalikan error
    HTTP yang jelas, bukan 500 Internal Server Error."""
    response = client.get("/api/search", params={"q": "hp murah", "mode": "semantic"})
    assert response.status_code in (200, 503)  # 200 jika model aktif, 503 jika tidak


def test_search_requires_query_param(client):
    response = client.get("/api/search", params={"mode": "bm25"})
    assert response.status_code == 422  # validasi Pydantic otomatis (Bagian 9.4)


def test_list_products_with_category_filter(client):
    response = client.get(
        "/api/products", params={"category": "Elektronik", "page_size": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert all(item["category"] == "Elektronik" for item in data["items"])


def test_get_product_not_found_returns_404(client):
    response = client.get("/api/products/P_TIDAK_ADA")
    assert response.status_code == 404


def test_similar_products_endpoint(client):
    list_response = client.get("/api/products", params={"page_size": 1})
    product_id = list_response.json()["items"][0]["product_id"]

    response = client.get(f"/api/recommendations/similar/{product_id}")
    assert response.status_code == 200
    assert response.json()["total_results"] >= 0


def test_recommendations_cold_start_user(client):
    response = client.get("/api/recommendations/user/U_BENAR_BENAR_BARU")
    assert response.status_code == 200
    assert response.json()["source"] == "cold_start_fallback"


def test_event_logging(client):
    response = client.post(
        "/api/events",
        json={
            "user_id": "U_TEST",
            "event_type": "product_click",
            "product_id": "P000001",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "logged"


def test_event_invalid_type_rejected(client):
    """event_type memakai Literal di Pydantic (Bagian 9.4) -- nilai di
    luar 5 tipe yang sah harus ditolak otomatis dengan 422."""
    response = client.post(
        "/api/events",
        json={"user_id": "U_TEST", "event_type": "tipe_tidak_valid"},
    )
    assert response.status_code == 422


def test_analytics_summary_structure(client):
    response = client.get("/api/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {
        "funnel",
        "click_through_rate",
        "top_queries",
        "top_categories",
    }


def test_experiment_assignment_is_deterministic(client):
    """Bagian 9.7.1: assignment A/B testing HARUS konsisten untuk user
    yang sama, dipanggil berkali-kali."""
    payload = {"experiment_id": "test_exp_pytest", "user_id": "U_CONSISTENT"}
    first = client.post("/api/experiments/assign", json=payload).json()["variant"]
    second = client.post("/api/experiments/assign", json=payload).json()["variant"]
    assert first == second
