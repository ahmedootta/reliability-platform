from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.ai_errors import AIError

# Our one error shape for the whole API: {"error": {"type": ..., "message": ...}}
HTTP_ERROR_TYPES = {
    404: ("not_found", "Route not found. See /docs for the available endpoints."),
    405: ("method_not_allowed", "This route does not support that HTTP method."),
}


# Our AI error type -> the HTTP status the client sees.
# auth_error is 502, never 401: the CLIENT did nothing wrong, our server's key is the problem.
AI_ERROR_STATUS = {
    "timeout": 504,         # Gateway Timeout: the upstream did not answer in time
    "rate_limited": 429,    # Too Many Requests
    "auth_error": 502,      # Bad Gateway: our key was refused upstream
    "upstream_error": 502,  # Bad Gateway: the provider is down or failed
    "bad_request": 400,     # the provider rejected what we sent
    "bad_output": 502,      # the provider answered, but not in a usable form
}


def error_response(status: int, error_type: str, message: str, **extra) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"type": error_type, "message": message, **extra}})


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    error_type, message = HTTP_ERROR_TYPES.get(exc.status_code, ("http_error", str(exc.detail)))
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"type": error_type, "message": message}},
        headers=getattr(exc, "headers", None),  # keeps e.g. the "Allow" header on 405
    )


async def ai_error_handler(request: Request, exc: AIError):
    return error_response(AI_ERROR_STATUS.get(exc.type, 502), exc.type, exc.message)


async def validation_error_handler(request: Request, exc: RequestValidationError):
    # Same shape as every other error; `fields` says which input was wrong and why.
    fields = [
        {"field": ".".join(str(part) for part in e["loc"][1:]) or e["loc"][0], "problem": e["msg"]}
        for e in exc.errors()
    ]
    return error_response(422, "invalid_input", "The request body is not valid.", fields=fields)


def register_exception_handlers(app: FastAPI) -> None:
    # Handles every HTTP error raised by the framework (404, 405) and by our own
    # `raise HTTPException(...)`, for all methods and all paths.
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(AIError, ai_error_handler)  # every AIError raised in a route
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # 422
