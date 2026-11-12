"""The ONE place that defines every error this API can return.

Each error is a class with: `status` (HTTP code), `type` (stable name the frontend
branches on, later also a metric label), `message` (safe to show a client), and
`description` (what Swagger says). From this single catalogue we get:

  1. the exceptions the code raises (ai_client.py, jobs.py)
  2. the JSON body the client receives:  {"error": {"type": ..., "message": ...}}
  3. the failure list in /docs (`error_responses`)

To add an error: add ONE class below. Handlers and docs pick it up on their own.
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas import ErrorResponse


class APIError(Exception):
    status = 500
    type = "internal_error"
    message = "Something went wrong on our side."
    description = "Unexpected server error."

    def __init__(self, message: str | None = None):
        self.message = message or self.message
        super().__init__(self.message)


# ---- the AI call failed (raised by ai_client.py / jobs.py) ----

class AIError(APIError):
    """Base of every AI failure. `except AIError` catches them all."""
    status = 502
    type = "ai_error"
    message = "The AI request failed."
    description = "The AI request failed."


class AITimeout(AIError):
    status = 504  # Gateway Timeout: the upstream did not answer in time
    type = "timeout"
    message = "The AI provider did not answer in time."
    description = "The AI provider did not answer in time."


class AIRateLimited(AIError):
    status = 429
    type = "rate_limited"
    message = "The AI provider is limiting requests. Try again later."
    description = "The AI provider is rate limiting us. Try again later."


class AIAuthError(AIError):
    status = 502  # never 401: the CLIENT did nothing wrong, OUR key was refused
    type = "auth_error"
    message = "The server could not authenticate with the AI provider."
    description = "Our server's key was refused by the AI provider (not the caller's fault)."


class AIUpstreamError(AIError):
    status = 502
    type = "upstream_error"
    message = "The AI provider is unavailable or returned an error."
    description = "The AI provider is down, unreachable, or failed."


class AIBadRequest(AIError):
    status = 400
    type = "bad_request"
    message = "The AI provider rejected the request."
    description = "The AI provider rejected the request."


class AIBadOutput(AIError):
    status = 502
    type = "bad_output"
    message = "The AI answered, but not in a usable form."
    description = "The AI answered, but not in a usable form (e.g. no allowed label)."


# ---- errors raised by the framework (never raised by our own code) ----

class InvalidInput(APIError):
    status = 422
    type = "invalid_input"
    message = "The request body is not valid."
    description = "The request body is not valid. `fields` says which input was wrong and why."


class NotFound(APIError):
    status = 404
    type = "not_found"
    message = "Route not found. See /docs for the available endpoints."
    description = "Unknown route."


class MethodNotAllowed(APIError):
    status = 405
    type = "method_not_allowed"
    message = "This route does not support that HTTP method."
    description = "The route exists, but not for this HTTP method."


def _all_errors(base: type[APIError] = APIError) -> list[type[APIError]]:
    found = []
    for sub in base.__subclasses__():
        found.append(sub)
        found.extend(_all_errors(sub))
    return found


# ---- the JSON body ----

def error_response(status: int, error_type: str, message: str, **extra) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"type": error_type, "message": message, **extra}})


# ---- handlers ----

async def api_error_handler(request: Request, exc: APIError):
    return error_response(exc.status, exc.type, exc.message)


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    known = {NotFound.status: NotFound, MethodNotAllowed.status: MethodNotAllowed}.get(exc.status_code)
    error_type, message = (known.type, known.message) if known else ("http_error", str(exc.detail))
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"type": error_type, "message": message}},
        headers=getattr(exc, "headers", None),  # keeps e.g. the "Allow" header on 405
    )


async def validation_error_handler(request: Request, exc: RequestValidationError):
    # `fields` says which input was wrong and why.
    fields = [
        {"field": ".".join(str(part) for part in e["loc"][1:]) or e["loc"][0], "problem": e["msg"]}
        for e in exc.errors()
    ]
    return error_response(InvalidInput.status, InvalidInput.type, InvalidInput.message, fields=fields)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(APIError, api_error_handler)  # our own errors, incl. every AIError
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # 404, 405, raise HTTPException
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # 422


# ---- Swagger ----

def error_responses(*statuses: int) -> dict:
    """The `responses=` argument of a route: lists each status with every error type that
    can produce it, built from the classes above (so docs can never drift from behaviour).
    Passing 422 also replaces FastAPI's default 422 shape with ours."""
    docs = {}
    for status in statuses:
        errors = [e for e in _all_errors() if e.status == status and e is not AIError]
        if not errors:
            raise ValueError(f"No error class has status {status}")
        examples = {}
        for e in errors:
            body = {"type": e.type, "message": e.message}
            if e is InvalidInput:
                body["fields"] = [{"field": "text", "problem": "String should have at least 1 character"}]
            examples[e.type] = {"summary": e.type, "value": {"error": body}}
        docs[status] = {
            "model": ErrorResponse,
            "description": "\n\n".join(f"**`{e.type}`**: {e.description}" for e in errors),
            "content": {"application/json": {"examples": examples}},
        }
    return docs
