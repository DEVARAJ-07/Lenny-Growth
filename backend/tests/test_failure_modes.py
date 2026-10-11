"""
Tests for failure modes, edge cases, and security boundaries.
"""
import pytest


@pytest.mark.asyncio
async def test_session_not_found_404(async_client):
    res = await async_client.get("/sessions/non-existent-session-id")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_empty_message_validation_error(async_client):
    # Create valid session
    sess_res = await async_client.post("/sessions", json={"title": "Test Error Session"})
    sess_id = sess_res.json()["id"]

    # Post empty message
    msg_res = await async_client.post(f"/sessions/{sess_id}/messages", json={"content": ""})
    assert msg_res.status_code == 422
    err_data = msg_res.json()
    assert "error" in err_data
    assert err_data["error"]["code"] == "VALIDATION_ERROR"
