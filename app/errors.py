from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# Our one error shape for the whole API: {"error": {"type": ..., "message": ...}}
HTTP_ERROR_TYPES = {
    404: ("not_found", "Route not found. See /docs for the available endpoints."),
    405: ("method_not_allowed", "This route does not support that HTTP method."),
}


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    error_type, message = HTTP_ERROR_TYPES.get(exc.status_code, ("http_error", str(exc.detail)))
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"type": error_type, "message": message}},
        headers=getattr(exc, "headers", None),  # keeps e.g. the "Allow" header on 405
    )


def register_exception_handlers(app: FastAPI) -> None:
    # Handles every HTTP error raised by the framework (404, 405) and by our own
    # `raise HTTPException(...)`, for all methods and all paths.
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
