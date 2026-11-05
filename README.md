# Reliability Platform (learning project)

A small server that calls an AI API, is monitored with **Prometheus**, and is visualised in **Grafana**.
It was built step by step to learn the flow and the concepts behind each piece.

1. **AI API server**: the server holds the API key and calls the AI API (request → response, success or failure)
2. **Prometheus**: the server exposes metrics; Prometheus scrapes and stores them
3. **Grafana**: a KPI dashboard on top of Prometheus, plus reading insights from it

- Plan: [PLAN.md](PLAN.md)
- Progress: [PROGRESS.md](PROGRESS.md)
- Learning notes and interview questions: [LEARNING.md](LEARNING.md)

## Running it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env              # then fill in your key
uvicorn app.main:app --reload     # http://localhost:8000/docs
pytest
```

Configuration lives in a local `.env` (copy `.env.example`). `.env` is git-ignored; never commit keys.

## License

MIT
