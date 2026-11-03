# Learning Log

This project is built to **understand**, not just to ship. The code gets written feature by feature; this file tracks what you have actually absorbed.

## How each feature works

1. Read the concept note in [learning/](learning/) (10–15 minutes).
2. Run the feature and break it on purpose.
3. **Teach-back**: answer the checkpoint questions in your own words in `notes/` (git-ignored). If you can't answer one, that's the gap to close before moving on.
4. Merge the PR, tick the box below.

## Progress

| # | Feature | Concept note | Read | Ran it | Teach-back |
|---|---|---|:-:|:-:|:-:|
| 0 | Foundation | [00 · How services talk](learning/00-how-services-talk.md) | ☐ | – | ☐ |
| 1 | Services | _coming_ | ☐ | ☐ | ☐ |
| 2 | CI | _coming_ | ☐ | ☐ | ☐ |
| 3 | Metrics | _coming_ | ☐ | ☐ | ☐ |
| 4 | SLOs + alerting | _coming_ | ☐ | ☐ | ☐ |
| 5 | Remediator | _coming_ | ☐ | ☐ | ☐ |
| 6 | Scheduled jobs | _coming_ | ☐ | ☐ | ☐ |
| 7 | Chaos + incidents | _coming_ | ☐ | ☐ | ☐ |
| 8 | Synthetic prober | _coming_ | ☐ | ☐ | ☐ |

## Interview question bank

Answer each one out loud in under 90 seconds. Tick when you can do it without notes.

**Reliability fundamentals**
- [ ] SLI vs SLO vs SLA: what's the difference?
- [ ] What is an error budget, and what happens when it runs out?
- [ ] Why alert on burn rate instead of error count?
- [ ] Why use two time windows for one alert?
- [ ] Liveness vs readiness: when do you restart, when not?
- [ ] Why does Prometheus pull instead of services pushing?
- [ ] What is high cardinality and why does it break Prometheus?
- [ ] Internal metrics vs the synthetic prober: what's the difference?
- [ ] Why does the availability SLI return no data at zero traffic, and what covers that gap?

**Automation and safety**
- [ ] How do you stop auto-remediation making an outage worse?
- [ ] Why is deduplication keyed on "open incident", not just the alert fingerprint?
- [ ] Why does the remediator need a socket proxy instead of the raw Docker socket?
- [ ] Why `restart: "no"` in the demo?
- [ ] Why is the verify step a separate delayed task rather than a sleep?

**Communication and architecture**
- [ ] Why is the remediator → worker hop asynchronous?
- [ ] What makes a webhook receiver safe to call twice?
- [ ] orders-api is slow: how do you prove payments is the cause?
- [ ] How would you scale this to 100 services?

**Scheduled jobs**
- [ ] How do you monitor a cron job that silently stops running?
- [ ] Cron vs Celery Beat: trade-offs?

**Incident response**
- [ ] Define MTTD and MTTR. How did you measure them?
- [ ] What goes in an incident report?
