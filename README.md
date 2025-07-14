# 📊 FastAPI Metrics App: Monitoring Documentation

This project is a containerized **FastAPI** application that exposes detailed system, process, HTTP, and database metrics using **Prometheus**. It can be deployed with **Docker Compose** and integrates with **Prometheus** for real-time monitoring.

---

## 🚀 Project Structure

```
fastapi-metrics-app/
├── app/
│   ├── Dockerfile
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── metrics/
│   │   ├── http_metrics.py
│   │   └── system_metrics.py
│   ├── middleware/
│   │   └── metrics_middleware.py
│   └── routers/
│       ├── api.py
│       └── health.py
├── .env
├── docker-compose.yml
├── prometheus.yml
└── requirements.txt
```

---

## 📦 Deployment Instructions

### 🔧 Build and Start the Application

```bash
docker-compose up --build
```

This will:

- Build Docker images (including FastAPI)
- Start services: FastAPI, PostgreSQL, Prometheus
- Run in detached mode

### 🛑 Stop the Application

```bash
docker-compose down
```

This stops and removes all containers, volumes, and networks.

---

## 💻 Application API Documentation

All API endpoints are available at:

```
Base URL: http://localhost:8000
```

---

## 🎠 Initial Data Setup

- On first startup, the `items` table is created automatically if it does not exist.
- **No initial data** is inserted.
- Use `POST /data` to add records.

---

## 📚 API Endpoints

### 1. Create Data

- **Endpoint**: `/data`
- **Method**: `POST`

#### Request Body

```json
{
  "name": "John Doe"
}
```

#### Response

```json
{
  "id": 1,
  "name": "John Doe"
}
```

### 2. Retrieve All Data

- **Endpoint**: `/data`
- **Method**: `GET`

#### Response

```json
[
  {
    "id": 1,
    "name": "John Doe"
  },
  {
    "id": 2,
    "name": "Jane Smith"
  }
]
```

### 3. Retrieve Single Data by ID

- **Endpoint**: `/data/{item_id}`
- **Method**: `GET`

#### Response

```json
{
  "id": 1,
  "name": "John Doe"
}
```

Or:

```json
{
  "detail": "Item not found"
}
```

### 4. Update Data

- **Endpoint**: `/data/{item_id}`
- **Method**: `PUT`

#### Request Body

```json
{
  "name": "Updated Name"
}
```

#### Response

```json
{
  "id": 1,
  "name": "Updated Name"
}
```

### 5. Delete Data

- **Endpoint**: `/data/{item_id}`
- **Method**: `DELETE`

#### Response

```json
{
  "message": "Item deleted successfully"
}
```

### 6. Application Metrics

- **Endpoint**: `/metrics`
- **Method**: `GET`

Returns Prometheus-compatible plaintext metrics.

### 7. Health Check

- **Endpoint**: `/health`
- **Method**: `GET`

#### Response

```json
{
  "status": "ok",
  "database": "connected",
}
```

---

## 📈 Prometheus Interface

Visit: [http://localhost:9090](http://localhost:9090)

---

## 🧠 CPU Metrics

| Metric Name                     | Type  | Description                                     |
|--------------------------------|-------|-------------------------------------------------|
| process_cpu_seconds_total      | Gauge | Total CPU time used by FastAPI process (seconds)|
| rate(process_cpu_seconds_total[5m]) | Gauge |         |

## 💾 Memory Metrics

| Metric Name                    | Type  | Description                                  |
|-------------------------------|-------|----------------------------------------------|
| process_resident_memory_bytes | Gauge | Physical RAM used by the FastAPI process     |
| process_virtual_memory_bytes  | Gauge | Total virtual memory allocated by process    |

## 🧵 System & Process Metrics

| Metric Name                | Type  | Description                                  |
|---------------------------|-------|----------------------------------------------|
| process_start_time_seconds| Gauge | Process start time (Unix timestamp)          |
| process_open_fds          | Gauge | Number of open file descriptors              |

## 🧹 Garbage Collection Metrics

| Metric Name                  | Type  | Description                                  |
|-----------------------------|-------|----------------------------------------------|
| python_gc_collections_total | Gauge | Total number of garbage collection runs      |

## 🌐 HTTP Request Metrics

| Metric Name                 | Type      | Description                                 | Labels                             |
|-----------------------------|-----------|---------------------------------------------|------------------------------------|
| http_requests_total         | Counter   | Total number of HTTP requests               | method, endpoint, status_code      ||           |
| http_response_size_bytes    | Histogram | Size of HTTP responses in bytes             | method, endpoint, status_code      |



## 📊 Example Prometheus Queries

### 1. Total HTTP Requests

```promql
http_requests_total
```

### 2. Average Request Duration (POST /data)

```promql
rate(http_request_duration_seconds_sum{method="POST", endpoint="/data"}[5m])
/
rate(http_request_duration_seconds_count{method="POST", endpoint="/data"}[5m])
```

---

## 🛠️ Troubleshooting

- **405 Error on /data/{id}**: Use proper method (PUT/DELETE) with tools like curl/Postman
- **Duplicated timeseries error**: Ensure `APP_REGISTRY` is used and not the default collector
- **Metrics not showing in Prometheus**:
  - Check FastAPI and Prometheus container logs
  - Confirm Prometheus target = `fastapi:8000`
  - Test `/metrics` locally in browser

---
