from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Score
from app.quiz_data import QUESTIONS, get_question_by_id, get_questions_public
from app.schemas import (
    PASS_THRESHOLD,
    AnswerResult,
    LeaderboardEntry,
    LeaderboardOut,
    QuizOut,
    SubmitRequest,
    SubmitResponse,
    WelcomeOut,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Claude Certified Architect Foundations Quiz API",
    description="API no oficial de práctica para el quiz CCA-F",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/welcome/{player_name}", response_model=WelcomeOut)
def welcome(player_name: str):
    name = player_name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="El nombre es obligatorio")
    return WelcomeOut(
        player_name=name,
        message=(
            f"¡Bienvenido/a, {name}! "
            "Prepárate para el quiz de Claude Certified Architect – Foundations. "
            "Son 10 preguntas de práctica sobre los 5 dominios del examen. ¡Éxito!"
        ),
    )


@app.get("/api/quiz", response_model=QuizOut)
def get_quiz():
    return QuizOut(
        title="Claude Certified Architect – Foundations (Práctica)",
        total=len(QUESTIONS),
        questions=get_questions_public(),
    )


@app.post("/api/quiz/submit", response_model=SubmitResponse)
def submit_quiz(payload: SubmitRequest, db: Session = Depends(get_db)):
    name = payload.player_name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="El nombre es obligatorio")
    if len(payload.answers) != len(QUESTIONS):
        raise HTTPException(
            status_code=400,
            detail=f"Se esperan {len(QUESTIONS)} respuestas",
        )

    seen: set[int] = set()
    results: list[AnswerResult] = []
    score = 0

    for answer in payload.answers:
        if answer.question_id in seen:
            raise HTTPException(
                status_code=400,
                detail=f"Respuesta duplicada para pregunta {answer.question_id}",
            )
        seen.add(answer.question_id)

        question = get_question_by_id(answer.question_id)
        if question is None:
            raise HTTPException(
                status_code=400,
                detail=f"Pregunta inválida: {answer.question_id}",
            )

        is_correct = answer.selected_index == question["correct_index"]
        if is_correct:
            score += 1

        results.append(
            AnswerResult(
                question_id=answer.question_id,
                correct=is_correct,
                correct_index=question["correct_index"],
                explanation=question["explanation"],
            )
        )

    total = len(QUESTIONS)
    percentage = round((score / total) * 100, 1)

    db_score = Score(player_name=name, score=score, total=total)
    db.add(db_score)
    db.commit()

    if percentage >= 80:
        message = f"¡Excelente, {name}! Dominas bien los fundamentos de CCA-F."
    elif percentage >= 60:
        message = f"Buen trabajo, {name}. Repasa las explicaciones y vuelve a intentarlo."
    else:
        message = (
            f"Ánimo, {name}. Revisa los dominios del examen y practica de nuevo."
        )

    return SubmitResponse(
        player_name=name,
        score=score,
        total=total,
        percentage=percentage,
        results=results,
        message=message,
    )


@app.get("/api/leaderboard", response_model=LeaderboardOut)
def leaderboard(limit: int = 10, db: Session = Depends(get_db)):
    limit = max(1, min(limit, 50))

    # Sub-query: best score per player, with most recent attempt as tie-breaker
    best_per_player = (
        db.query(
            Score.player_name,
            func.max(Score.score).label("best_score"),
        )
        .group_by(Score.player_name)
        .subquery()
    )

    # Join back to get the full row for the best attempt per player.
    # When a player has multiple rows with the same best score, pick the
    # most recent one (max created_at).
    rows = (
        db.query(Score)
        .join(
            best_per_player,
            (Score.player_name == best_per_player.c.player_name)
            & (Score.score == best_per_player.c.best_score),
        )
        .order_by(desc(Score.score), desc(Score.created_at))
        .all()
    )

    # Deduplicate in Python in case a player has multiple rows with the
    # same best score (keep only the most recent one).
    seen: set[str] = set()
    unique_rows: list[Score] = []
    for row in rows:
        if row.player_name not in seen:
            seen.add(row.player_name)
            unique_rows.append(row)

    # Apply limit after deduplication
    unique_rows = unique_rows[:limit]

    entries = []
    for idx, row in enumerate(unique_rows):
        percentage = round((row.score / row.total) * 100, 1) if row.total else 0
        entries.append(
            LeaderboardEntry(
                rank=idx + 1,
                player_name=row.player_name,
                score=row.score,
                total=row.total,
                percentage=percentage,
                passed=percentage >= PASS_THRESHOLD,
                pass_threshold=PASS_THRESHOLD,
                created_at=row.created_at,
            )
        )
    return LeaderboardOut(entries=entries)
