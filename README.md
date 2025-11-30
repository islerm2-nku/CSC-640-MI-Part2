# iRacing Telemetry API - Phase 2

FastAPI-based telemetry API with OAuth authentication.

## Features

- FastAPI REST API
- MySQL database for telemetry storage
- OAuth authentication
- JWT token-based authorization
- Docker containerized deployment

## Quick Start

```bash
# Build and start containers
docker compose up --build

# Verify tables were created
docker compose exec db bash -c 'mysql -uappuser -papppass -D app -e "SHOW TABLES;"'
```

## Project Structure

```
CSC-640-MI-Part2/
├── app/            # FastAPI application code
├── db/             # Database migrations
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml  # Python dependencies
```

## Development

- FastAPI runs on port 80 with hot reload enabled
- Python debugger available on port 5678
- MySQL exposed on port 3306
