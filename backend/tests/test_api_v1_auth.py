import pytest
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_verify_auth_success(client, db_session):
    # Mock data
    payload = {"init_data": "valid_init_data"}
    mock_user_data = {
        "id": 12345678,
        "first_name": "John",
        "last_name": "Doe"
    }
    
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.role = "admin"
    
    # Path to patch needs to be where the function is used, or the original module
    with patch("app.api.v1.auth.verify_telegram_init_data", return_value=mock_user_data), \
         patch("app.api.v1.auth.get_or_create_user", return_value=mock_user), \
         patch("app.api.v1.auth.create_access_token", return_value="fake_token"):
        
        response = await client.post("/api/v1/auth/verify", json=payload)
        
        assert response.status_code == 200
        assert response.json() == {
            "access_token": "fake_token", 
            "role": "admin",
            "token_type": "bearer"
        }

@pytest.mark.asyncio
async def test_verify_auth_invalid_data(client):
    payload = {"init_data": "invalid_init_data"}
    
    with patch("app.api.v1.auth.verify_telegram_init_data", return_value=None):
        response = await client.post("/api/v1/auth/verify", json=payload)
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Невалідні дані Telegram"
