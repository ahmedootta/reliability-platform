# Reliability Platform (learning project)

A small FastAPI server that calls an AI API (two job endpoints: `/classify` on a light model, `/analyze` on a heavy one), is monitored with **Prometheus**, and is visualised in **Grafana**. Built step by step to learn the flow and the concepts.

- Plan: [PLAN.md](PLAN.md)
- Progress: [PROGRESS.md](PROGRESS.md)
- Learning notes and interview questions: [LEARNING.md](LEARNING.md)

## Running it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env              # then fill in your key
uvicorn app.main:app --reload     # Swagger UI: http://localhost:8000/docs
pytest
```

Configuration lives in a local `.env` (copy `.env.example`). `.env` is git-ignored; never commit keys.

## License

MIT
