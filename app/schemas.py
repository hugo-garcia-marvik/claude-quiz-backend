from datetime import datetime

from pydantic import BaseModel, Field


class QuestionOut(BaseModel):
    id: int
    domain: str
    question: str
    options: list[str]


class QuizOut(BaseModel):
    title: str
    total: int
    questions: list[QuestionOut]


class AnswerItem(BaseModel):
    question_id: int
    selected_index: int = Field(ge=0, le=3)


class SubmitRequest(BaseModel):
    player_name: str = Field(max_length=80)
    answers: list[AnswerItem]


class AnswerResult(BaseModel):
    question_id: int
    correct: bool
    correct_index: int
    explanation: str


class SubmitResponse(BaseModel):
    player_name: str
    score: int
    total: int
    percentage: float
    results: list[AnswerResult]
    message: str


class LeaderboardEntry(BaseModel):
    rank: int
    player_name: str
    score: int
    total: int
    percentage: float
    created_at: datetime


class LeaderboardOut(BaseModel):
    entries: list[LeaderboardEntry]


class WelcomeOut(BaseModel):
    message: str
    player_name: str
