from fastapi import FastAPI

app = FastAPI(title="AI API Server")


@app.get("/health")
def health():
    return {"status": "ok"}
