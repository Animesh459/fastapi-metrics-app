import time
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.metrics.http_metrics import http_requests_total, http_request_duration_seconds, http_request_size_bytes, http_response_size_bytes

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        method = request.method
        path = request.url.path

        # Exclude metrics endpoint from being tracked by itself to avoid recursion
        if path == "/metrics":
            return await call_next(request)

        start_time = time.time()

        # Try to get request body size (approximate for streaming)
        request_body_size = 0
        if request.headers.get("content-length"):
            try:
                request_body_size = int(request.headers["content-length"])
            except ValueError:
                pass # Ignore if not a valid integer

        response = await call_next(request)

        process_time = time.time() - start_time
        status_code = response.status_code

        # Update HTTP request total counter
        http_requests_total.labels(method=method, endpoint=path, status_code=status_code).inc()

        # Update HTTP request duration histogram
        http_request_duration_seconds.labels(method=method, endpoint=path).observe(process_time)

        # Update request size histogram
        http_request_size_bytes.labels(method=method, endpoint=path).observe(request_body_size)

        # Update response size histogram (approximate, more accurate would require reading the body)
        response_body_size = 0
        if response.headers.get("content-length"):
            try:
                response_body_size = int(response.headers["content-length"])
            except ValueError:
                pass
        http_response_size_bytes.labels(method=method, endpoint=path, status_code=status_code).observe(response_body_size)

        return response