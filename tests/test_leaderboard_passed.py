"""Tests for DFT-206: Add passed flag to LeaderboardEntry schema."""

from datetime import datetime, timedelta, timezone

from app.schemas import PASS_THRESHOLD
from tests.conftest import _seed_score


class TestLeaderboardPassedFlag:
    """Leaderboard entries include passed boolean and pass_threshold."""

    def test_passed_true_when_above_threshold(self, client, db_session):
        """Player with percentage >= PASS_THRESHOLD has passed=True."""
        # 7/10 = 70% which equals the 70% threshold
        _seed_score(db_session, "Alice", score=7, total=10)

        resp = client.get("/api/leaderboard")
        entries = resp.json()["entries"]

        assert len(entries) == 1
        assert entries[0]["passed"] is True
        assert entries[0]["percentage"] == 70.0

    def test_passed_false_when_below_threshold(self, client, db_session):
        """Player with percentage < PASS_THRESHOLD has passed=False."""
        # 6/10 = 60% which is below 70% threshold
        _seed_score(db_session, "Alice", score=6, total=10)

        resp = client.get("/api/leaderboard")
        entries = resp.json()["entries"]

        assert len(entries) == 1
        assert entries[0]["passed"] is False
        assert entries[0]["percentage"] == 60.0

    def test_pass_threshold_included(self, client, db_session):
        """Every leaderboard entry includes the pass_threshold value."""
        _seed_score(db_session, "Alice", score=8, total=10)

        resp = client.get("/api/leaderboard")
        entries = resp.json()["entries"]

        assert len(entries) == 1
        assert entries[0]["pass_threshold"] == PASS_THRESHOLD

    def test_mixed_passed_and_failed(self, client, db_session):
        """Leaderboard correctly flags both passing and failing players."""
        now = datetime.now(timezone.utc)
        _seed_score(
            db_session, "Alice", score=9, total=10, created_at=now - timedelta(hours=2)
        )  # 90% -> passed
        _seed_score(
            db_session, "Bob", score=5, total=10, created_at=now - timedelta(hours=1)
        )  # 50% -> failed
        _seed_score(
            db_session, "Charlie", score=7, total=10, created_at=now
        )  # 70% -> passed

        resp = client.get("/api/leaderboard")
        entries = resp.json()["entries"]

        assert len(entries) == 3
        # Sorted by score desc: Alice (9), Charlie (7), Bob (5)
        assert entries[0]["player_name"] == "Alice"
        assert entries[0]["passed"] is True
        assert entries[1]["player_name"] == "Charlie"
        assert entries[1]["passed"] is True
        assert entries[2]["player_name"] == "Bob"
        assert entries[2]["passed"] is False

    def test_threshold_boundary_exact(self, client, db_session):
        """Exactly at threshold is considered passed."""
        # PASS_THRESHOLD is 70.0; 7/10 = 70.0%
        _seed_score(db_session, "BoundaryPlayer", score=7, total=10)

        resp = client.get("/api/leaderboard")
        entries = resp.json()["entries"]

        assert entries[0]["passed"] is True
        assert entries[0]["percentage"] == PASS_THRESHOLD

    def test_threshold_just_below(self, client, db_session):
        """Just below threshold is considered not passed."""
        # 69/100 = 69.0% which is below 70%
        # With total=10, closest below 70% is 6/10 = 60%
        _seed_score(db_session, "JustBelow", score=6, total=10)

        resp = client.get("/api/leaderboard")
        entries = resp.json()["entries"]

        assert entries[0]["passed"] is False

    def test_passed_uses_best_score_after_dedup(self, client, db_session):
        """Passed flag is based on the best score, not worst or latest."""
        now = datetime.now(timezone.utc)
        # First attempt: 5/10 = 50% (fail)
        _seed_score(
            db_session, "Alice", score=5, total=10, created_at=now - timedelta(hours=2)
        )
        # Second attempt: 8/10 = 80% (pass) — this is the best
        _seed_score(
            db_session, "Alice", score=8, total=10, created_at=now - timedelta(hours=1)
        )
        # Third attempt: 6/10 = 60% (fail)
        _seed_score(db_session, "Alice", score=6, total=10, created_at=now)

        resp = client.get("/api/leaderboard")
        entries = resp.json()["entries"]

        assert len(entries) == 1
        assert entries[0]["score"] == 8
        assert entries[0]["passed"] is True

    def test_pass_threshold_constant_value(self):
        """PASS_THRESHOLD is 70.0 as per spec."""
        assert PASS_THRESHOLD == 70.0

    def test_schema_has_passed_and_threshold_fields(self):
        """LeaderboardEntry schema includes passed and pass_threshold."""
        from app.schemas import LeaderboardEntry

        fields = LeaderboardEntry.model_fields
        assert "passed" in fields
        assert "pass_threshold" in fields

    def test_zero_total_not_passed(self, client, db_session):
        """Edge case: if total is 0, percentage is 0 and passed is False."""
        _seed_score(db_session, "Edge", score=0, total=0)

        resp = client.get("/api/leaderboard")
        entries = resp.json()["entries"]

        assert len(entries) == 1
        assert entries[0]["percentage"] == 0
        assert entries[0]["passed"] is False
