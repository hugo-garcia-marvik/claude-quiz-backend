"""Tests for DFT-200: Return 400 when player name is empty after strip."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# /api/welcome/{player_name}
# ---------------------------------------------------------------------------


def test_welcome_empty_name_returns_400():
    """Completely empty path segment should return 400."""
    resp = client.get("/api/welcome/%20")  # single space URL-encoded
    assert resp.status_code == 400
    assert resp.json()["detail"] == "El nombre es obligatorio"


def test_welcome_whitespace_only_returns_400():
    """Whitespace-only name should return 400 after strip."""
    resp = client.get("/api/welcome/%20%20%20")  # three spaces
    assert resp.status_code == 400
    assert resp.json()["detail"] == "El nombre es obligatorio"


def test_welcome_valid_name_returns_200():
    """A valid name (non-empty after strip) should return 200."""
    resp = client.get("/api/welcome/Ana")
    assert resp.status_code == 200
    body = resp.json()
    assert body["player_name"] == "Ana"
    assert "Ana" in body["message"]


def test_welcome_name_with_surrounding_spaces_is_trimmed():
    """Name with leading/trailing spaces should be trimmed."""
    resp = client.get("/api/welcome/%20Ana%20")
    assert resp.status_code == 200
    assert resp.json()["player_name"] == "Ana"


# ---------------------------------------------------------------------------
# /api/quiz/submit
# ---------------------------------------------------------------------------

def _make_answers():
    """Build a valid answers payload (all selecting index 0)."""
    return [{"question_id": i, "selected_index": 0} for i in range(1, 11)]


def test_submit_empty_name_returns_400():
    """Empty player_name string should return 400."""
    resp = client.post(
        "/api/quiz/submit",
        json={"player_name": "", "answers": _make_answers()},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "El nombre es obligatorio"


def test_submit_whitespace_only_name_returns_400():
    """Whitespace-only player_name should return 400 after strip."""
    resp = client.post(
        "/api/quiz/submit",
        json={"player_name": "   ", "answers": _make_answers()},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "El nombre es obligatorio"


def test_submit_valid_name_returns_200():
    """A valid name should pass validation and return results."""
    resp = client.post(
        "/api/quiz/submit",
        json={"player_name": "Ana", "answers": _make_answers()},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["player_name"] == "Ana"


def test_submit_name_with_spaces_is_trimmed():
    """Name with leading/trailing spaces should be trimmed."""
    resp = client.post(
        "/api/quiz/submit",
        json={"player_name": "  Ana  ", "answers": _make_answers()},
    )
    assert resp.status_code == 200
    assert resp.json()["player_name"] == "Ana"
