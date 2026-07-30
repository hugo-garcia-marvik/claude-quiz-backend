# Claude Quiz Backend

## Stack overview

This is a monolithic REST API built with FastAPI and Python 3.11+, using SQLAlchemy 2.x as the ORM and SQLite for persistent storage of quiz scores. Pydantic v2 handles request/response validation and settings management, while Uvicorn serves the ASGI application. The architecture is layered: routes → schemas → business logic → ORM → database, with dependency injection wiring database sessions into handlers.

## Active skills

| Skill | Purpose | Category |
|---|---|---|
| `fastapi-endpoint` | Build production-ready FastAPI endpoints with async patterns, Pydantic validation, and dependency injection for database access | Backend |
| `python-patterns` | Apply Python-specific design decisions for async handling, type hints, project structure, and testing strategy | Language |
| `senior-backend` | Implement scalable API design, database optimization, and performance tuning principles | Architecture |
| `clean-code` | Write maintainable code following SRP, DRY, KISS with clear naming and focused functions | Quality |
| `software-architecture` | Apply Clean Architecture and Domain-Driven Design principles to API structure and module organization | Architecture |
| `test-driven-development` | Write comprehensive pytest tests before or alongside implementation to ensure correctness | Quality |
| `code-reviewer` | Review code for best practices, security, and quality standards across the codebase | Quality |
| `senior-qa` | Build test suites, analyze coverage, and establish testing strategy for the API | Quality |
| `supabase-postgres-best-practices` | Optimize database queries and schema design (applicable if migrating from SQLite to PostgreSQL) | Data |
| `senior-data-engineer` | Design efficient data pipelines for score persistence and query optimization | Data |

## Cross-skill patterns

- **backend-data-pipeline**: Combine `fastapi-endpoint`, `senior-backend`, `python-patterns`, and `test-driven-development` to ensure the score persistence layer is robust, testable, and performant.
- **code-quality-architecture**: Use `clean-code`, `code-reviewer`, `software-architecture`, and `test-driven-development` to enforce consistent standards across routes, models, and schemas.

## Architectural notes

- Use `fastapi-endpoint` with `python-patterns` to design async-friendly route handlers; ensure database session injection via `Depends(get_db)` follows FastAPI's dependency system precisely.
- Pair `senior-backend` with `supabase-postgres-best-practices` when optimizing queries; currently SQLite is acceptable for local dev, but schema and query patterns should be portable to PostgreSQL for production.
- Apply `clean-code` principles to route handlers by extracting complex business logic (e.g., score calculation, answer validation) into helper functions in separate modules, keeping routes thin.
- Use `test-driven-development` with `fastapi-endpoint` to write pytest fixtures for the test database and dependency override before implementing new endpoints; this prevents regressions and clarifies requirements.
- Implement `code-reviewer` practices in pull requests to catch common FastAPI pitfalls: improper async/await usage, missing type hints, and unvalidated Pydantic models.
- Leverage `software-architecture` to maintain clear separation between `models.py` (ORM), `schemas.py` (API contracts), and `quiz_data.py` (domain logic); resist the urge to mix concerns.

## Gotchas

- `fastapi-endpoint` requires explicit async/await handling in route handlers; blocking I/O in sync functions will starve the event loop.
- SQLite's transaction handling differs from PostgreSQL; if migrating, review `supabase-postgres-best-practices` for concurrent write scenarios.
- Pydantic v2 changed validation behavior and error messages; ensure all schemas use explicit `model_validate()` or `model_dump()` calls rather than deprecated v1 patterns.
- The `get_questions_public()` function must always strip `correct_index` and `explanation` before sending to the frontend; this is a security boundary—test it explicitly.
- Session cleanup via `SessionLocal` context managers is critical; leaked sessions can cause file locking issues on SQLite.