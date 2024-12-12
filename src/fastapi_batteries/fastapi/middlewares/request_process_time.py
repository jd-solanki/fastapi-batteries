import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp


class RequestProcessTimeMiddleware(BaseHTTPMiddleware):
    """Middleware to measure and add the processing time of a request to the response headers.

    This middleware calculates the time taken to process a request and adds this duration
    to the response headers under the key "X-Process-Time".
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = time.perf_counter() - start_time

        # Add the processing time to the response & convert to milliseconds for better readability
        response.headers["X-Process-Time"] = f"{process_time * 1000:.2f}ms"

        return response
