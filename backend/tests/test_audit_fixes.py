import pytest
import time
from app.services.auth_service import verify_telegram_init_data, MAX_INIT_DATA_AGE
from unittest.mock import patch

def test_verify_telegram_init_data_expired():
    # Mocking time to be in the future relative to auth_date
    auth_date = int(time.time()) - MAX_INIT_DATA_AGE - 10
    init_data = f"auth_date={auth_date}&hash=dummy"
    
    with patch("hmac.compare_digest", return_value=True):
        result = verify_telegram_init_data(init_data)
        assert result is None

def test_verify_telegram_init_data_valid_age():
    auth_date = int(time.time()) - 100
    init_data = f"auth_date={auth_date}&user=%7B%22id%22%3A123%7D&hash=dummy"
    
    with patch("hmac.compare_digest", return_value=True):
        # We also need to mock the secret key generation to not fail on missing BOT_TOKEN
        with patch("app.services.auth_service.hmac.new") as mock_hmac:
            mock_hmac.return_value.hexdigest.return_value = "dummy"
            result = verify_telegram_init_data(init_data)
            assert result == {"id": 123}

from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import require_admin
from app.models.user import User

client = TestClient(app)

def test_export_report_path_traversal():
    # Mocking admin user
    mock_admin = User(id=1, telegram_id=123, role="admin", is_active=True)
    app.dependency_overrides[require_admin] = lambda: mock_admin
    
    # Mocking build_report_sync to return a suspicious path
    with patch("app.api.v1.reports.build_report_sync", return_value="/etc/passwd"):
        response = client.post(
            "/api/v1/reports/export",
            json={"date_from": "2026-05-01", "date_to": "2026-05-02"}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Недозволений шлях"
    
    app.dependency_overrides.clear()
