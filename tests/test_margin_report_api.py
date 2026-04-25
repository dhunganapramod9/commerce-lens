from fastapi.testclient import TestClient

from commercelens.api.main import app


def test_demo_margin_report_json_endpoint() -> None:
    response = TestClient(app).get("/v1/margin-report/demo")

    assert response.status_code == 200
    payload = response.json()
    assert payload["store_name"] == "Demo Store"
    assert payload["unsafe_matches_count"] == 1
    assert payload["safe_raise_count"] == 1


def test_demo_margin_report_html_endpoint() -> None:
    response = TestClient(app).get("/v1/margin-report/demo.html")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Demo Store Margin Leak Report" in response.text
    assert "This Week's Actions" in response.text
