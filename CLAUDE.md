# CLAUDE.md

This is a **learning project**: a small AI API server, monitored by Prometheus, visualised in Grafana. Understanding matters more than speed. See [PLAN.md](PLAN.md) for the full plan.

## Instructions

1. **Always update the docs after any change.** After any step, code change, decision, or answered question, update both:
   - [PROGRESS.md](PROGRESS.md): tick the finished step and add a row to the session log.
   - [LEARNING.md](LEARNING.md): add the flow, where it lives in the code, concepts, gotchas, and the user's questions with answers.

   Do this in the same piece of work as the change, not later.

## Working style

- Go one step at a time (the numbered steps in PLAN.md). Make each step runnable before moving on.
- After each step, explain the flow and where the code lives, and invite questions.
- At the end of each part, add 10–15 interview questions (hands-on and concepts) to LEARNING.md.
- Keep explanations simple and in plain words.

## Git

- One branch per part: `feat/ai-api-server`, then `feat/prometheus-metrics`, then `feat/grafana-dashboard`.
- Commit, push, and open PRs whenever the user asks, and only then. Do not do any of them on my own.
- Never commit `.env` or any real API key.
