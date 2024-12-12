from typing import Any

from fastapi import Request
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp


# Utility class to track the number of queries for each request
class QueryCounter:
    def __init__(self) -> None:
        self.query_count = 0

    def increment(self):
        self.query_count += 1

    def get_count(self):
        return self.query_count


# Middleware to track DB hits per request
class QueryCountMiddleware(BaseHTTPMiddleware):
    """Middleware to count the number of database queries executed during the handling of a request."""

    def __init__(self, app: ASGIApp, engine: AsyncEngine) -> None:
        super().__init__(app)
        self.engine = engine

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        query_counter = QueryCounter()  # Create a fresh query counter for each request

        # Attach query tracking to the session
        def before_cursor_execute(*args: Any, **kwargs: Any) -> None:  # noqa: ANN401, ARG001
            query_counter.increment()

        # Register the event listener locally for this request
        event.listen(self.engine.sync_engine, "before_cursor_execute", before_cursor_execute)

        # Proceed with the request and get the response
        response = await call_next(request)

        # Log the number of queries executed
        query_count = query_counter.get_count()
        print(f"Number of queries executed: {query_count}")

        # Add the query count to the response headers
        response.headers["X-DB-Query-Count"] = str(query_count)

        # Clean up: remove the event listener to avoid memory leaks
        event.remove(self.engine.sync_engine, "before_cursor_execute", before_cursor_execute)

        return response
