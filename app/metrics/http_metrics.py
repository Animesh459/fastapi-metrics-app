from prometheus_client import Counter, Histogram

# Counter for total HTTP requests
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests.',
    ['method', 'endpoint', 'status_code']
)

# Histogram for request durations
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'Histogram of HTTP request durations in seconds.',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, float('inf'))
)

# Optional: Histograms for request and response sizes
http_request_size_bytes = Histogram(
    'http_request_size_bytes',
    'Histogram of HTTP request sizes in bytes.',
    ['method', 'endpoint'],
    buckets=(100, 500, 1000, 5000, 10000, 50000, 100000, float('inf'))
)

http_response_size_bytes = Histogram(
    'http_response_size_bytes',
    'Histogram of HTTP response sizes in bytes.',
    ['method', 'endpoint', 'status_code'],
    buckets=(100, 500, 1000, 5000, 10000, 50000, 100000, float('inf'))
)