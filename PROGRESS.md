# Progress

Status key: ⬜ not started · 🚧 in progress · ✅ done

## Part 1: AI API server 🚧

- [x] 1.1 Project skeleton + `/health`
- [ ] 1.2 Config and secrets (`.env`)
- [ ] 1.3 AI client + `/ask` (real and fake mode)
- [ ] 1.4 Model routing (light / heavy)
- [ ] 1.5 Failure handling (timeout, 401, 429, 5xx)
- [ ] 1.6 Tests
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

| Date | What we did | Open questions |
|---|---|---|
| 2026-11-04 | Reset the project and wrote the new plan, progress, and learning files | – |
| 2026-11-05 | Chose Groq (`openai/gpt-oss-20b`), set up `.env`, built step 1.1 (venv, FastAPI, `/health`, test), wrote the FastAPI revision | One client or many? (answered: one, reused) |
| 2026-11-05 | Added light/heavy model routing to the plan (step 1.4); wrote "how to create a FastAPI project" in LEARNING.md; committed and pushed | – |
