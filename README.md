# Lyftr Backend Assignment

This repository contains the backend service developed for the Lyftr internship assignment.

The service receives webhook messages, stores them safely, exposes query APIs, health checks,
analytics, and metrics. The project is fully containerized using Docker.

This is a **backend-only service** (no UI).

---

## Tech Stack

- Python 3.10
- FastAPI
- SQLite
- Docker & Docker Compose
- Prometheus metrics

---

## Project Structure

lyftr-backend-assignment/
│
├── app/
│ ├── main.py # FastAPI application & API routes
│ ├── models.py # Pydantic data models
│ ├── storage.py # SQLite persistence logic
│ ├── metrics.py # Prometheus metrics
│ ├── logging_utils.py # Structured logging helpers
│ └── config.py # Environment configuration
│
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
└── README.md


---

## Running the Application

### Using Docker (Recommended)

docker compose up --build


The application will be available at:

http://localhost:8000/


### Using Makefile

make build
make up


To stop the services:
make down


To view logs:
make logs


---

## Health Check Endpoints

These endpoints are required for container orchestration and monitoring.

### Liveness Probe

GET /health/live

Response:
{"status":"live"}


### Readiness Probe

GET /health/ready


Response:
{"status":"ready"}


---

## Webhook Endpoint

### Endpoint


POST /webhook


### Features

- Validates HMAC signature
- Prevents duplicate message insertion
- Persists valid messages to storage
- Returns appropriate HTTP status codes

---

## Metrics Endpoint

### Endpoint

GET /metrics


### Description

Exposes Prometheus-compatible metrics including:

- Request count
- Request latency
- Webhook processing statistics



