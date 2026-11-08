"""Our own error types for AI calls.

The rest of the app never sees Groq's exceptions, only these. Each has a short
`type` (used in the JSON error body and later as a metric label) and a message that
is safe to show to a client (never contains the key, the prompt, or provider details).
"""


class AIError(Exception):
    type = "ai_error"
    message = "The AI request failed."

    def __init__(self, message: str | None = None):
        self.message = message or self.message
        super().__init__(self.message)


class AITimeout(AIError):
    type = "timeout"
    message = "The AI provider did not answer in time."


class AIRateLimited(AIError):
    type = "rate_limited"
    message = "The AI provider is limiting requests. Try again later."


class AIAuthError(AIError):
    type = "auth_error"
    message = "The server could not authenticate with the AI provider."


class AIUpstreamError(AIError):
    type = "upstream_error"
    message = "The AI provider is unavailable or returned an error."


class AIBadRequest(AIError):
    type = "bad_request"
    message = "The AI provider rejected the request."


class AIBadOutput(AIError):
    type = "bad_output"
    message = "The AI answered, but not in a usable form."
