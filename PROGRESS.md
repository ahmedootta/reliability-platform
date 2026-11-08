# Progress

Status key: ⬜ not started · 🚧 in progress · ✅ done

## Part 1: AI API server 🚧

- [x] 1.1 Project skeleton + `/health`
- [x] 1.2 Config and secrets (`.env`) + custom 404/405
- [x] 1.3 AI client: `ai_client.py`, `jobs.py`, `schemas.py`, `ai_errors.py`; verified live
- [ ] 1.4 Job endpoints `/classify` (light) and `/analyze` (heavy): 🚧 stubs exist, you are writing them; not wired to the client yet
- [ ] 1.5 HTTP error handling (AI errors to 504/429/502/400, 422 in our shape)
- [ ] 1.6 Route tests
- [ ] 1.7 Swagger documentation (examples, error responses); base setup done
- [ ] Learning notes written
- [ ] Discussion / Q&A done
- [ ] Interview questions answered (0 / 15)

## Part 2: Prometheus monitoring ⬜

- [ ] 2.1 `prometheus_client` + `/metrics`
- [ ] 2.2 Metrics defined and recorded
- [ ] 2.3 Prometheus in Docker, target UP
- [ ] 2.4 PromQL in the UI and CLI
- [ ] 2.5 Logs vs metrics (structured logs)
- [ ] Learning notes written
- [ ] Discussion / Q&A done
- [ ] Interview questions answered (0 / 15)

## Part 3: Grafana dashboard and insights ⬜

- [ ] 3.1 Grafana + Prometheus datasource
- [ ] 3.2 KPI panels built in the UI
- [ ] 3.3 Dashboard exported and provisioned as code
- [ ] 3.4 Grafana CLI / HTTP API
- [ ] 3.5 Traffic generator
- [ ] 3.6 Insights exercise
- [ ] Learning notes written
- [ ] Discussion / Q&A done
- [ ] Interview questions answered (0 / 15)

## Session log

| Date | What we did | Open |
|---|---|---|
| 2026-11-04 | Reset the repo; wrote the plan, progress, and learning files | – |
| 2026-11-05 | Chose Groq and set up `.env`; step 1.1 (venv, FastAPI, `/health`, first test); revised FastAPI, uvicorn, routers; you split the routes into `app/routes/` | – |
| 2026-11-07 | Step 1.2: `config.py` with fail-fast `lifespan`, `.env` path fix, custom 404/405; measured sync vs async; explained middleware and Starlette | – |
| 2026-11-08 | Swagger base setup; decided the endpoint picks the tier (`/classify` light, `/analyze` heavy); step 1.3: AI client verified live (classify 0.4 s, analyze 2.2 s), 28 tests; rewrote the docs by topic and removed `/ask`; fixed `main.py` imports and tags after the `ask` route was deleted | – |
