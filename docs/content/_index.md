---
title: "Home"
date: 2025-11-30
draft: false
---

# iRacing Telemetry API Documentation

Welcome to the documentation for the iRacing Telemetry API (CSC-640-MI-Part2).

## Overview

A FastAPI-based telemetry API with GitHub OAuth authentication for uploading, storing, and analyzing iRacing telemetry data.

## Features

- ✅ **FastAPI Framework** - Modern, fast Python web framework
- ✅ **GitHub OAuth** - Secure authentication with JWT tokens
- ✅ **Telemetry Upload** - Parse and store .ibt files
- ✅ **Lap Analysis** - Automatic lap detection and incident tracking
- ✅ **Statistical Analysis** - Built-in metrics and averages
- ✅ **Interactive Docs** - Swagger UI and ReDoc
- ✅ **Docker Deployment** - Fully containerized

## Quick Links

- [GitHub Repository](https://github.com/islerm2-nku/CSC-640-MI-Part2)
- [API Documentation (Local)](http://localhost/docs) - Available when running locally
- [Presentations](/presentations/) - Slide decks and guides

## Tech Stack

- **Backend**: FastAPI, Python 3.11+
- **Database**: MySQL 8.0 with SQLAlchemy ORM
- **Authentication**: GitHub OAuth + JWT
- **Telemetry Parser**: Python irsdk
- **Deployment**: Docker & Docker Compose

## Quick Start

```bash
# Clone the repository
git clone https://github.com/islerm2-nku/CSC-640-MI-Part2.git
cd CSC-640-MI-Part2

# Start with the setup script
./setup.sh

# Or manually
docker compose up --build -d
```

Access the API at http://localhost and interactive docs at http://localhost/docs

## Documentation

- [Presentations](/presentations/) - API Overview and Deployment Guide slides
- [README](https://github.com/islerm2-nku/CSC-640-MI-Part2/blob/main/README.md) - Project README

## Project Structure

```
CSC-640-MI-Part2/
├── app/                    # FastAPI application
│   ├── routers/           # API endpoints
│   │   ├── auth.py       # OAuth authentication
│   │   ├── telemetry.py  # File upload
│   │   └── sessions.py   # Session/lap management
│   ├── services/          # Business logic
│   ├── models.py          # SQLAlchemy models
│   └── main.py           # Application entry point
├── db/                    # Database utilities
├── telemetry/            # Example .ibt files
├── docker-compose.yml    # Container orchestration
├── setup.sh             # Quick start script
└── docs/                # Hugo documentation site
```

## Contact

- **Author**: Mitchell Isler
- **GitHub**: [islerm2-nku](https://github.com/islerm2-nku)
- **Repository**: [CSC-640-MI-Part2](https://github.com/islerm2-nku/CSC-640-MI-Part2)
