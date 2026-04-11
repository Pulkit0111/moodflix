from unittest.mock import patch
import pytest
from fastapi import HTTPException
from app.dependencies import verify_firebase_token

@pytest.mark.asyncio
async def test_verify_token_valid():
    mock_decoded = {"uid": "user123", "name": "Test User", "email": "test@example.com"}
    with patch("app.dependencies.firebase_auth") as mock_auth:
        mock_auth.verify_id_token.return_value = mock_decoded
        result = await verify_firebase_token(authorization="Bearer valid-token")
        assert result["uid"] == "user123"

@pytest.mark.asyncio
async def test_verify_token_missing_header():
    with pytest.raises(HTTPException) as exc_info:
        await verify_firebase_token(authorization=None)
    assert exc_info.value.status_code == 401

@pytest.mark.asyncio
async def test_verify_token_invalid():
    with patch("app.dependencies.firebase_auth") as mock_auth:
        mock_auth.verify_id_token.side_effect = Exception("Invalid token")
        with pytest.raises(HTTPException) as exc_info:
            await verify_firebase_token(authorization="Bearer bad-token")
        assert exc_info.value.status_code == 401
