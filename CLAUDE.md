# CLAUDE.md

This is a **learning project**: a small AI API server, monitored by Prometheus, visualised in Grafana. Understanding matters more than speed. See [PLAN.md](PLAN.md) for the full plan.

## Instructions

1. **Always update the docs after any change.** After any step, code change, decision, or answered question, update both:
   - [PROGRESS.md](PROGRESS.md): tick the finished step and add a row to the session log.
   - [LEARNING.md](LEARNING.md): put the flow, code location, concepts, and gotchas in the topic section they belong to, and add a one-line entry to the questions index for each question the user asked.

   Do this in the same piece of work as the change, not later.
2. **Keep the docs short.** Each fact lives in one place. Update the existing section instead of appending a new one. LEARNING.md is organised by topic, not by date, and holds the answers (its questions index only points to them). The session log in PROGRESS.md has one row per day or milestone. Before adding text, check whether it is already there.

## Working style

- Go one step at a time (the numbered steps in PLAN.md). Make each step runnable before moving on.
- After each step, explain the flow and where the code lives, and invite questions.
- At the end of each part, add 10–15 interview questions (hands-on and concepts) to LEARNING.md.
- Keep explanations simple and in plain words.

## Git

- One branch per part: `feat/ai-api-server`, then `feat/prometheus-metrics`, then `feat/grafana-dashboard`.
- Commit, push, and open PRs whenever the user asks, and only then. Do not do any of them on my own.
- Never commit `.env` or any real API key.
