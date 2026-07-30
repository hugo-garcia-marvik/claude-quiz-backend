# Claude Quiz Backend — Product Summary

## Project Name
**Claude Quiz Backend**

## Overview
Claude Quiz Backend is an unofficial REST API that powers a practice quiz application for the **Claude Certified Architect – Foundations (CCA-F)** certification exam. It delivers randomized practice questions, evaluates submitted answers, and maintains a scored leaderboard — giving candidates a structured way to self-assess their readiness before the real exam.

> **Disclaimer:** This project is community-built and is not affiliated with or endorsed by Anthropic.

---

## Key Features

| Feature | Description |
|---|---|
| **Practice Quiz Delivery** | Serves a set of 10 carefully curated multiple-choice questions covering the official CCA-F exam domains |
| **Server-Side Answer Validation** | Correct answers are never sent to the client; validation happens exclusively on the server, preventing answer leakage |
| **Automatic Score Calculation** | Calculates the player's raw score and percentage after each submission |
| **Contextual Feedback** | Provides personalized encouragement messages based on performance (Excellent / Good Work / Keep Trying) |
| **Leaderboard** | Tracks and ranks top performers, allowing candidates to compare scores with peers |
| **Detailed Answer Review** | After submission, players receive per-question feedback including the correct answer and an explanation |
| **Interactive API Docs** | Swagger/OpenAPI UI is automatically available at `/docs` for easy exploration |

---

## Target Users

- **Developer-learners** preparing to sit the Anthropic Claude Certified Architect – Foundations (CCA-F) exam
- **Educators and bootcamp instructors** who want to embed a practice quiz in a custom frontend application
- **Frontend developers** who need a ready-made quiz API to build a study-tool UI on top of

---

## Value Proposition

The CCA-F certification validates knowledge of building production-grade applications with Claude. Candidates benefit from structured, exam-style practice before the real test. This backend provides:

- A **realistic exam simulation** with questions drawn from all five official exam domains
- A **secure design** that prevents answer leakage to the client
- A **plug-and-play API** that any frontend (React, Vue, plain HTML, etc.) can consume immediately
- A **competitive element** (leaderboard) that motivates repeat practice

---

## Core Workflows

### 1. Taking a Quiz
1. A player visits the frontend and optionally enters their name.
2. The frontend calls `GET /api/quiz` to fetch 10 questions (without correct answers).
3. The player reads each question and selects one of four options.
4. On completion, the frontend calls `POST /api/quiz/submit` with the player's name and all selected answers.
5. The server validates each answer, calculates the total score, and returns detailed per-question feedback along with an overall feedback message.

### 2. Checking the Leaderboard
1. The frontend calls `GET /api/leaderboard` (optionally with a `limit` query parameter, 1–50).
2. The server returns the top performers ranked by score descending (then by submission time as a tiebreaker).
3. The player can see where they stand relative to other candidates.

### 3. Health Monitoring
- Operators or monitoring tools call `GET /health` to verify the service is running correctly.

---

## Exam Domain Coverage

The 10 practice questions are distributed across the five official CCA-F exam domains:

| Domain | Weight | Questions Covered |
|---|---|---|
| Agentic Architecture & Orchestration | 27% | Hub-and-spoke patterns, agent loop termination |
| Tool Design & MCP Integration | 18% | Tool design best practices, Model Context Protocol |
| Claude Code Configuration & Workflows | 20% | CLAUDE.md hierarchy, non-interactive mode |
| Prompt Engineering & Structured Output | 20% | Structured output robustness, production prompt design |
| Context Management & Reliability | 15% | Context limit strategies, graceful degradation |
