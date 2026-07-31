"""Tests for DFT-202: Tiebreak leaderboard by created_at DESC (most recent wins)."""

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Score

# Use an in-memory SQLite database for isolation
TEST_DATABASE_URL = "sqlite:///./test_leaderboard.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function():
    """Re-create tables before each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_function():
    """Drop tables after each test."""
    Base.metadata.drop_all(bind=engine)


def test_leaderboard_tiebreak_most_recent_first():
    """When two players have the same score, the most recent attempt ranks higher."""
    now = datetime.now(timezone.utc)
    earlier = now - timedelta(hours=2)
    later = now - timedelta(hours=1)

    db = TestingSessionLocal()
    db.add(Score(player_name="OldPlayer", score=8, total=10, created_at=earlier))
    db.add(Score(player_name="NewPlayer", score=8, total=10, created_at=later))
    db.commit()
    db.close()

    resp = client.get("/api/leaderboard")
    assert resp.status_code == 200
    entries = resp.json()["entries"]
    assert len(entries) == 2
    # Most recent attempt should be first
    assert entries[0]["player_name"] == "NewPlayer"
    assert entries[0]["rank"] == 1
    assert entries[1]["player_name"] == "OldPlayer"
    assert entries[1]["rank"] == 2


def test_leaderboard_score_desc_takes_priority():
    """Higher score always wins regardless of timestamp."""
    now = datetime.now(timezone.utc)
    earlier = now - timedelta(hours=2)
    later = now - timedelta(hours=1)

    db = TestingSessionLocal()
    # Lower score but more recent
    db.add(Score(player_name="LowRecent", score=5, total=10, created_at=later))
    # Higher score but older
    db.add(Score(player_name="HighOld", score=9, total=10, created_at=earlier))
    db.commit()
    db.close()

    resp = client.get("/api/leaderboard")
    assert resp.status_code == 200
    entries = resp.json()["entries"]
    assert entries[0]["player_name"] == "HighOld"
    assert entries[1]["player_name"] == "LowRecent"


def test_leaderboard_three_way_tie():
    """Three players with the same score are ordered by most recent first."""
    now = datetime.now(timezone.utc)

    db = TestingSessionLocal()
    db.add(Score(player_name="A", score=7, total=10, created_at=now - timedelta(hours=3)))
    db.add(Score(player_name="B", score=7, total=10, created_at=now - timedelta(hours=1)))
    db.add(Score(player_name="C", score=7, total=10, created_at=now - timedelta(hours=2)))
    db.commit()
    db.close()

    resp = client.get("/api/leaderboard")
    assert resp.status_code == 200
    entries = resp.json()["entries"]
    names = [e["player_name"] for e in entries]
    assert names == ["B", "C", "A"]
