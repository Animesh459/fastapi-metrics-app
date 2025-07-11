# FastAPI Metrics Monitoring System

This project implements a comprehensive FastAPI application that exposes system-level and application-level metrics in Prometheus format for real-time monitoring.

## Project Overview

The application demonstrates how to integrate Prometheus client library with FastAPI to track key performance indicators, including CPU usage, memory consumption, HTTP request patterns, and database interactions.

## Objectives

* **Production-ready FastAPI application:** Built with robust error handling and structured for maintainability.
* **System Resource Monitoring:** Tracks CPU utilization, memory usage (resident, virtual), process start time, file descriptor usage, and thread count.
* **HTTP Request Patterns:** Monitors total HTTP requests, request durations, and optional request/response sizes, all categorized by method, endpoint, and status code.
* **Real-time Observability:** Provides a `/metrics` endpoint that Prometheus can scrape for real-time insights.
* **Scalable Monitoring Architecture:** Designed to work seamlessly with Prometheus and Grafana for a complete monitoring solution.

## Technical Stack

* **Core Framework:**
    * **FastAPI:** High-performance web framework.
    * **Python 3.9+:** Runtime environment.
    * **Uvicorn:** ASGI server for production.
* **Monitoring Stack:**
    * **Prometheus Client:** Python library for metrics collection.
    * **Prometheus:** Time-series database for metrics storage and querying.
* **Database:**
    * **PostgreSQL:** Relational database for data storage (`asyncpg` for async access).
* **Utilities:**
    * **psutil:** For system-level process information.
    * **secure:** For adding security headers.

## Architecture Design

The application follows a modular architecture: