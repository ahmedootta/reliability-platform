# Progress

Status key: ⬜ not started · 🚧 in progress · ✅ done

## Part 1: AI API server 🚧

- [x] 1.1 Project skeleton + `/health`
- [x] 1.2 Config and secrets (`.env`) + custom 404/405
- [x] 1.3 AI client: `ai_client.py`, `jobs.py`, `schemas.py`; verified live
- [x] 1.4 Job endpoints `/classify` (light) and `/analyze` (heavy), verified live
- [x] 1.5 HTTP error handling (AI errors to 504/429/502/400, 422 in our shape)
- [x] 1.6 Route tests (success, validation, and every failure; 47 tests)
- [x] 1.7 Swagger documentation (request/response examples, error responses)
- [x] Learning notes written
- [ ] Discussion / Q&A done
- [ ] Interview questions answered (1 / 15)

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
| 2026-11-09 | Pushed the AI layer and docs. Step 1.4: `/classify` and `/analyze` routes wired to schemas, `jobs.py` and the client; 11 route tests (39 total); live check on real Groq | AI failures return a plain 500 until step 1.5 |
| 2026-11-09 | Replaced the three separate flow diagrams in LEARNING.md with one end-to-end flow (startup, request, failures) and explained `lifespan` | – |
| 2026-11-08 | Pushed routes. Could not reproduce 0 tokens on `/analyze` (8 live calls fine). Step 1.5/1.6: `AIError` and 422 handlers in `errors.py`, `AI_ERROR_STATUS` map, `__fail:bad_output__` marker, failure route tests; fixed `pick_label` matching "a" inside "cannot" | 0-token report: waiting for the exact response and log line |
| 2026-11-08 | Pushed step 1.5. Step 1.7: error responses and examples in Swagger (`error_responses()` helper), 3 new tests (50 total). All coding steps of Part 1 done | Part 1 interview questions |
| 2026-11-08 | Refactor: merged `ai_errors.py`, the status map and the Swagger error text into one catalogue in `errors.py` (class per error); docs generated from it; 53 tests | – |
| 2026-11-11 | Wrote the 15 Part 1 interview questions (12 FastAPI, 3 AI API) | You answer them; then Part 2 |
