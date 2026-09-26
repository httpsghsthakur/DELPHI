# DELPHI Docker Deployment Guide

## Architecture
The DELPHI Docker deployment consists of three services coordinated via Docker Compose:
- **db**: PostgreSQL database for persistent storage of forecasts, events, and analyses.
- **backend**: FastAPI service running the DELPHI inference pipeline (EventEmbed, EventNet, CredNet, CausalSeq).
- **frontend**: React SPA served via Nginx, which also acts as a reverse proxy routing `/api/` traffic to the backend.

## Prerequisites
- Docker Engine 20.10+
- Docker Compose v2+
- At least 8GB RAM (16GB recommended for model loading)

## Setup Instructions

1. **Configuration:**
   Copy the example environment file:
   ```bash
   cp .env.docker.example .env
   ```
   Update `.env` with a strong `POSTGRES_PASSWORD`.

2. **Artifact Provisioning:**
   Ensure your model checkpoints and retrieval indexes are placed in the `models/` and `indexes/` directories at the project root. The backend container mounts these directories read-only.
   
   Expected structure:
   - `models/registry.json`
   - `models/tokenizer/`
   - `models/eventembed/weights.pt`
   - `models/eventnet/weights.pt`
   - `models/crednet/weights.pt`
   - `models/causalseq/weights.pt`
   - `indexes/retrieval.idx`
   - `indexes/metadata.json`

3. **Start the Deployment:**
   ```bash
   docker compose up --build -d
   ```

4. **Verify Health:**
   Backend readiness check:
   ```bash
   curl http://localhost:8000/health/ready
   ```

## URLs
- **Frontend Dashboard:** http://localhost:8080
- **API Base:** http://localhost:8000
- **OpenAPI Docs:** http://localhost:8000/docs

## Volumes & Persistence
- **pgdata:** Named volume holding PostgreSQL data. Survives container restarts.
- **logs:** Bind-mounted directory for application logs.
- **models & indexes:** Bind-mounted read-only directories.

## Backup and Restore
To backup the database:
```bash
docker compose exec -T db pg_dump -U delphi delphidb > backup.sql
```
To restore:
```bash
cat backup.sql | docker compose exec -T db psql -U delphi delphidb
```
