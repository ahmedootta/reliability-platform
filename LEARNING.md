# Learning

Filled in as we go. Each part has the same sections:

- **The flow**: what happens, step by step, when a request comes in
- **Where it lives in the code**: file → responsibility
- **Concepts**: short explanations in plain words
- **Gotchas**: things that broke or surprised us
- **Your questions**: questions you asked during the part, with the answers
- **Interview questions**: 10–15 at the end of the part. Answer each one out loud in under 90 seconds, then tick it.

---

## Part 1: AI API server

### FastAPI in 10 minutes (quick revision)

FastAPI is a Python web framework. You write normal functions; it turns them into HTTP endpoints.

| Piece | What it is | Example in our code |
|---|---|---|
| `app = FastAPI()` | The application object. Everything attaches to it. | [app/main.py](app/main.py) |
| Route decorator | `@app.get("/health")` links an HTTP method + path to a function. Also `@app.post`, etc. | `health()` |
| Return value | Return a dict or a model; FastAPI converts it to JSON with status 200. | `{"status": "ok"}` |
| Pydantic model | A class describing the shape of a request or response body. FastAPI validates incoming JSON against it and returns **422** if it doesn't match. | `AskRequest` (step 1.3) |
| `response_model` | Filters and documents what we send back, so extra or secret fields never leak. | step 1.3 |
| `HTTPException` | Raise it to return an error status + JSON body (e.g. 502, 504). | step 1.4 |
| Dependency injection | `Depends(...)` lets FastAPI supply shared things (settings, the AI client) to a route. Easy to swap in tests. | step 1.2/1.3 |
| `def` vs `async def` | `def` runs in a thread pool; `async def` runs on the event loop and must never block (no slow sync calls inside it). | decided in step 1.3 |
| Auto docs | `/docs` (Swagger UI) is generated from your routes and models. | open `localhost:8000/docs` |
| Server | FastAPI only defines the app. **uvicorn** is the server process that listens on a port and runs it. | `uvicorn app.main:app` |
| Testing | `TestClient(app)` calls the app in-process, with no real server needed. | [tests/test_health.py](tests/test_health.py) |

### How to create a FastAPI project (manual vs commands)

**FastAPI has no project generator.** There is no `django-admin startproject` and no `manage.py`. A FastAPI project is just Python files, so doing it by hand is the normal way, and it is exactly what we did in step 1.1.

Django vs FastAPI:

| | Django | FastAPI |
|---|---|---|
| Create project | `django-admin startproject` generates a fixed layout | You create the folders and files yourself |
| Structure | Imposed by the framework | Your choice |
| Run | `python manage.py runserver` | `uvicorn app.main:app --reload` |
| Included | ORM, admin, auth, templates | Routing, validation, docs. Everything else you add |

Steps (what we did):
1. `python3 -m venv .venv` then `source .venv/bin/activate`: an isolated environment.
2. `pip install fastapi "uvicorn[standard]"`, then `pip freeze` or a hand-written `requirements.txt`.
3. Create the `app/` folder with an empty `__init__.py` (it makes `app` an importable package).
4. Create `app/main.py` containing `app = FastAPI()` and at least one route.
5. Run `uvicorn app.main:app --reload`. Read it as `uvicorn <module path>:<variable name>`: file `app/main.py`, variable `app`.
6. Open `/docs` to try the routes.

**Can you run it with `python main.py`?** Yes. Add this at the bottom of `main.py`:
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", reload=True)
```
That is the same uvicorn, started from Python. Running `uvicorn ...` from the terminal is more common, and it lets you pass `--port` and `--workers` without editing code.

There is also an official `fastapi` command (`fastapi dev app/main.py`) that wraps uvicorn. It is a convenience, not a project generator.

Growing structure (we add these only when needed):
```
app/
  main.py      # creates the app, includes routers
  config.py    # settings
  router.py    # model routing
  ai_client.py # the only file that talks to the AI API
  routes/      # (later) one file per group of endpoints, using APIRouter
```

### Model routing: light vs heavy

Real AI products rarely send every request to the biggest model. Big models are slower, cost more, and hit rate limits sooner. So the server picks a **tier** per job:

| Tier | Model (Groq) | Use for | Trade-off |
|---|---|---|---|
| light | `openai/gpt-oss-20b` | Classification, short answers, simple extraction | Fast, cheap, weaker reasoning |
| heavy | `openai/gpt-oss-120b` | Multi-step reasoning, long answers | Slower, more expensive, better quality |

Where it lives: `router.py` has one small function, `tier -> model name`, reading `AI_MODEL_LIGHT` and `AI_MODEL_HEAVY` from `.env`. The route calls the router and passes the chosen model to `ai_client.py`. The client stays the same; only the model argument changes. This is the "one client, model per call" idea from above. In Part 2 every metric gets a `tier` label, so in Grafana we can compare latency, errors and cost of light vs heavy.

### Step 1.1: skeleton and `/health`

#### The flow
1. You run `uvicorn app.main:app --reload`. uvicorn imports `app` from `app/main.py` and listens on port 8000.
2. `curl localhost:8000/health` sends `GET /health`.
3. uvicorn passes the request to FastAPI, which finds the route that matches `GET /health`.
4. FastAPI calls `health()`, converts the returned dict to JSON, and sends `200 {"status":"ok"}`.

#### Where it lives in the code
| File | Responsibility |
|---|---|
| [app/main.py](app/main.py) | The FastAPI app and routes |
| [tests/test_health.py](tests/test_health.py) | Calls `/health` with `TestClient` |
| [pytest.ini](pytest.ini) | Puts the project root on the import path so tests can `import app` |
| [requirements.txt](requirements.txt) | Dependencies, installed into `.venv/` |
| `.env` / [.env.example](.env.example) | Local settings and the key (`.env` is git-ignored) |

#### Run it
```bash
source .venv/bin/activate
uvicorn app.main:app --reload      # then open http://localhost:8000/docs
pytest                             # run the tests
```

### Concepts
- **Why a venv:** `.venv/` keeps this project's packages separate from the rest of your system.
- **Why `/health`:** a cheap endpoint that says "the process is up". Monitoring tools and Docker use it. It is a different thing from "the AI API works".
- **Key vs model:** the API key says *who you are*; the model says *which model answers*. They are separate settings in `.env`.
- **One client, reused:** the Groq client holds the key, the connection pool, the timeout and the retries, so it is created **once** at startup and reused. Model, `temperature` and `max_completion_tokens` are arguments to each call, so they can change per request. Change the key in `.env` and you restart the server.

### Gotchas
- `pytest` failed with `No module named 'app'` until `pytest.ini` added `pythonpath = .`. Pytest does not add the project root to the import path by default.
- `.env` values have no quotes and no spaces around `=`.

### Your questions
- **Q: Do I create a new client every time I change the model or other settings?**
  A: No. Create the client once and reuse it. Model, temperature and token limits are per-call arguments. Only a new key (or timeout/retry settings on the client) needs a restart.

### Interview questions
_Added at the end of Part 1._

---

## Part 2: Prometheus monitoring

### The flow
_To be written._

### Where it lives in the code
_To be written._

### Concepts
_To be written._

### Gotchas
_To be written._

### Your questions
_None yet._

### Interview questions
_Added at the end of Part 2._

---

## Part 3: Grafana dashboard and insights

### The flow
_To be written._

### Where it lives in the code
_To be written._

### Concepts
_To be written._

### Dashboard insights (your findings)
_Written during step 3.6._

### Your questions
_None yet._

### Interview questions
_Added at the end of Part 3._
