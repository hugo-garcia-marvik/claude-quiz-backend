"""Shared test fixtures for the quiz API test suite."""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Score

# Use an in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite://"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test and drop them afterwards."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def db_session():
    """Provide a transactional database session for tests."""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    """FastAPI test client with overridden DB dependency."""
    from fastapi.testclient import TestClient

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _seed_score(
    db_session,
    player_name: str,
    score: int,
    total: int = 10,
    created_at: datetime | None = None,
) -> Score:
    """Helper to insert a Score row for tests."""
    if created_at is None:
        created_at = datetime.now(timezone.utc)
    row = Score(
        player_name=player_name,
        score=score,
        total=total,
        created_at=created_at,
    )
    db_session.add(row)
    db_session.commit()
    db_session.refresh(row)
    return row
