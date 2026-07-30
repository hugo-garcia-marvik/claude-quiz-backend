# Claude Quiz Backend

API de práctica para el **Claude Certified Architect – Foundations (CCA-F)**.

## Stack

- Python 3.11+
- FastAPI
- SQLAlchemy + SQLite
- Uvicorn

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/api/welcome/{player_name}` | Mensaje de bienvenida |
| `GET` | `/api/quiz` | 10 preguntas (sin respuestas correctas) |
| `POST` | `/api/quiz/submit` | Enviar respuestas y guardar puntaje |
| `GET` | `/api/leaderboard` | Top líderes por puntaje |

## Arranque

```bash
cd claude-quiz-backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Ejemplo de submit

```bash
curl -X POST http://localhost:8000/api/quiz/submit \
  -H "Content-Type: application/json" \
  -d '{
    "player_name": "Hugo",
    "answers": [
      {"question_id": 1, "selected_index": 1},
      {"question_id": 2, "selected_index": 1},
      {"question_id": 3, "selected_index": 1},
      {"question_id": 4, "selected_index": 1},
      {"question_id": 5, "selected_index": 1},
      {"question_id": 6, "selected_index": 1},
      {"question_id": 7, "selected_index": 1},
      {"question_id": 8, "selected_index": 1},
      {"question_id": 9, "selected_index": 1},
      {"question_id": 10, "selected_index": 1}
    ]
  }'
```

## Nota

Material de estudio **no oficial**, no afiliado a Anthropic.
