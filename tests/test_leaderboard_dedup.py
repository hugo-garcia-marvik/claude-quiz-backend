"""Tests for DFT-204: Deduplicate leaderboard to best score per player."""

from datetime import datetime, timedelta, timezone

from tests.conftest import _seed_score


class TestLeaderboardDeduplication:
    """Leaderboard returns only the best attempt per player."""

    def test_single_player_multiple_attempts_keeps_best(self, client, db_session):
        """When a player has multiple attempts, only the best score appears."""
        now = datetime.now(timezone.utc)
        _seed_score(db_session, "Alice", score=5, created_at=now - timedelta(hours=2))
        _seed_score(db_session, "Alice", score=8, created_at=now - timedelta(hours=1))
        _seed_score(db_session, "Alice", score=6, created_at=now)

        resp = client.get("/api/leaderboard")
        assert resp.status_code == 200
        entries = resp.json()["entries"]

        assert len(entries) == 1
        assert entries[0]["player_name"] == "Alice"
        assert entries[0]["score"] == 8
        assert entries[0]["rank"] == 1

    def test_multiple_players_best_per_each(self, client, db_session):
        """Each player appears once with their best score."""
        now = datetime.now(timezone.utc)
        _seed_score(db_session, "Alice", score=7, created_at=now - timedelta(hours=3))
        _seed_score(db_session, "Alice", score=9, created_at=now - timedelta(hours=2))
        _seed_score(db_session, "Bob", score=10, created_at=now - timedelta(hours=1))
        _seed_score(db_session, "Bob", score=6, created_at=now)

        resp = client.get("/api/leaderboard")
        entries = resp.json()["entries"]

        assert len(entries) == 2
        # Bob (10) first, Alice (9) second
        assert entries[0]["player_name"] == "Bob"
        assert entries[0]["score"] == 10
        assert entries[0]["rank"] == 1
        assert entries[1]["player_name"] == "Alice"
        assert entries[1]["score"] == 9
        assert entries[1]["rank"] == 2

    def test_tie_breaker_most_recent(self, client, db_session):
        """When two players have the same best score, most recent first."""
        now = datetime.now(timezone.utc)
        _seed_score(db_session, "Alice", score=8, created_at=now - timedelta(hours=2))
        _seed_score(db_session, "Bob", score=8, created_at=now - timedelta(hours=1))

        resp = client.get("/api/leaderboard")
        entries = resp.json()["entries"]

        assert len(entries) == 2
        # Bob is more recent with same score
        assert entries[0]["player_name"] == "Bob"
        assert entries[1]["player_name"] == "Alice"

    def test_same_player_same_best_score_keeps_most_recent(self, client, db_session):
        """When a player has multiple attempts with the same best score,
        the most recent attempt is shown."""
        now = datetime.now(timezone.utc)
        _seed_score(db_session, "Alice", score=8, created_at=now - timedelta(hours=2))
        _seed_score(db_session, "Alice", score=8, created_at=now)

        resp = client.get("/api/leaderboard")
        entries = resp.json()["entries"]

        assert len(entries) == 1
        assert entries[0]["player_name"] == "Alice"
        assert entries[0]["score"] == 8

    def test_contiguous_ranks(self, client, db_session):
        """Ranks are contiguous (1, 2, 3) after deduplication."""
        now = datetime.now(timezone.utc)
        _seed_score(db_session, "Alice", score=10, created_at=now - timedelta(hours=3))
        _seed_score(db_session, "Alice", score=5, created_at=now - timedelta(hours=2))
        _seed_score(db_session, "Bob", score=7, created_at=now - timedelta(hours=1))
        _seed_score(db_session, "Bob", score=3, created_at=now)
        _seed_score(db_session, "Charlie", score=9, created_at=now)

        resp = client.get("/api/leaderboard")
        entries = resp.json()["entries"]

        assert len(entries) == 3
        ranks = [e["rank"] for e in entries]
        assert ranks == [1, 2, 3]
        # Alice (10), Charlie (9), Bob (7)
        assert entries[0]["player_name"] == "Alice"
        assert entries[1]["player_name"] == "Charlie"
        assert entries[2]["player_name"] == "Bob"

    def test_limit_applied_after_dedup(self, client, db_session):
        """Limit is applied after deduplication, not before."""
        now = datetime.now(timezone.utc)
        for i in range(5):
            name = f"Player{i}"
            # Each player gets two attempts
            _seed_score(
                db_session, name, score=i, created_at=now - timedelta(hours=i * 2)
            )
            _seed_score(
                db_session,
                name,
                score=i + 1,
                created_at=now - timedelta(hours=i * 2 + 1),
            )

        resp = client.get("/api/leaderboard?limit=3")
        entries = resp.json()["entries"]

        # Should have 3 unique players, not 3 raw rows
        assert len(entries) == 3
        player_names = [e["player_name"] for e in entries]
        assert len(set(player_names)) == 3

    def test_empty_leaderboard(self, client, db_session):
        """Empty leaderboard returns empty entries."""
        resp = client.get("/api/leaderboard")
        assert resp.status_code == 200
        assert resp.json()["entries"] == []

    def test_percentage_calculated_correctly(self, client, db_session):
        """Percentage is calculated from best score."""
        _seed_score(db_session, "Alice", score=7, total=10)
        _seed_score(db_session, "Alice", score=3, total=10)

        resp = client.get("/api/leaderboard")
        entries = resp.json()["entries"]

        assert len(entries) == 1
        assert entries[0]["percentage"] == 70.0
