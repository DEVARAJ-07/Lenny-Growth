"""
Tests for Sessions API endpoints.
"""
import pytest


@pytest.mark.asyncio
async def test_session_lifecycle(async_client):
    # 1. Create session
    create_res = await async_client.post("/sessions", json={
        "title": "Growth Framework Session",
        "provider": "ollama",
        "model": "qwen2.5:3b"
    })
    assert create_res.status_code == 200
    sess_data = create_res.json()
    assert sess_data["title"] == "Growth Framework Session"
    assert "id" in sess_data
    session_id = sess_data["id"]

    # 2. List sessions
    list_res = await async_client.get("/sessions")
    assert list_res.status_code == 200
    sessions = list_res.json()
    assert any(s["id"] == session_id for s in sessions)

    # 3. Get session detail
    detail_res = await async_client.get(f"/sessions/{session_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == session_id
    assert isinstance(detail["messages"], list)

    # 4. Delete session
    del_res = await async_client.delete(f"/sessions/{session_id}")
    assert del_res.status_code == 200

    # 5. Verify deleted
    verify_res = await async_client.get(f"/sessions/{session_id}")
    assert verify_res.status_code == 404
