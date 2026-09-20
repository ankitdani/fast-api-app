from prometheus_client import Counter, Histogram
import time


REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests",
    ["method", "path", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP request latency",
    ["method", "path"]
)

async def track_metrics(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    REQUEST_COUNT.labels(method=request.method, path=request.url.path, status=response.status_code).inc()
    REQUEST_LATENCY.labels(method=request.method, path=request.url.path).observe(duration)

    return response

