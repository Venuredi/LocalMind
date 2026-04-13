# LocalMind Docker Setup Guide

This guide will help you run LocalMind Code Intelligence using Docker.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- At least 8GB of available RAM (for Phi3 model)
- 10GB of free disk space

## Quick Start

### 1. Build and Start Services

```bash
# Clone the repository (if not already done)
cd /path/to/code-intelligence

# Start all services
docker-compose up -d
```

This will start:
- LocalMind application on `http://localhost:8000`
- Ollama service on `http://localhost:11434`

### 2. Install Phi3 Model in Ollama

After the containers are running, install the Phi3 model:

```bash
# Execute command in the ollama container
docker exec -it localmind-ollama ollama pull phi3:mini
```

Wait for the model to download (approximately 2-3 GB).

### 3. Verify Setup

Check if everything is running:

```bash
# Check container status
docker-compose ps

# Check application health
curl http://localhost:8000/api/health

# Check Ollama status
curl http://localhost:11434/api/tags
```

### 4. Access the Application

Open your browser and navigate to:
```
http://localhost:8000
```

## Configuration

### Custom Repository Path

To index a specific repository, set the `REPO_PATH` environment variable:

```bash
REPO_PATH=/path/to/your/repo docker-compose up -d
```

Or edit `docker-compose.yml` and update the volume mount:

```yaml
volumes:
  - /absolute/path/to/your/repo:/workspace:ro
```

### GPU Support (Optional)

If you have an NVIDIA GPU and want to use it for faster LLM inference:

1. Install [nvidia-docker](https://github.com/NVIDIA/nvidia-docker)
2. Uncomment the GPU section in `docker-compose.yml`:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

3. Restart the services:
```bash
docker-compose down
docker-compose up -d
```

## Managing Services

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f localmind
docker-compose logs -f ollama
```

### Stop Services

```bash
docker-compose stop
```

### Start Services

```bash
docker-compose start
```

### Restart Services

```bash
docker-compose restart
```

### Remove Everything

```bash
# Stop and remove containers, networks
docker-compose down

# Also remove volumes (WARNING: deletes all data)
docker-compose down -v
```

## Troubleshooting

### Ollama Connection Issues

If LocalMind can't connect to Ollama:

```bash
# Check if Ollama is running
docker exec -it localmind-ollama ollama list

# Restart Ollama
docker-compose restart ollama
```

### Application Not Starting

Check logs for errors:

```bash
docker-compose logs localmind
```

Common issues:
- **Port 8000 already in use**: Stop other services or change port in `docker-compose.yml`
- **Out of memory**: Increase Docker memory limit in Docker Desktop settings

### Model Not Found

If you get "Phi3 model not available" errors:

```bash
# Verify Phi3 is installed
docker exec -it localmind-ollama ollama list

# If not listed, install it
docker exec -it localmind-ollama ollama pull phi3:mini
```

### Rebuild After Code Changes

```bash
docker-compose build localmind
docker-compose up -d
```

## Data Persistence

Data is persisted in the following locations:

- **Application data**: `./data/index.json` (mounted volume)
- **Ollama models**: `ollama-data` Docker volume

To backup data:

```bash
# Backup application data
cp ./data/index.json ./backup/

# Backup Ollama models
docker run --rm -v localmind_ollama-data:/data -v $(pwd):/backup alpine tar czf /backup/ollama-backup.tar.gz -C /data .
```

## Production Deployment

For production environments:

1. Use environment variables for sensitive configuration
2. Enable HTTPS with a reverse proxy (nginx, Traefik)
3. Set up monitoring and logging
4. Configure resource limits in `docker-compose.yml`:

```yaml
services:
  localmind:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## Alternative: Docker Build Only

If you want to run Ollama separately (e.g., on a different machine):

```bash
# Build the image
docker build -t localmind:latest .

# Run with custom Ollama host
docker run -d \
  -p 8000:8000 \
  -e OLLAMA_HOST=http://your-ollama-host:11434 \
  -v $(pwd)/data:/app/data \
  localmind:latest
```

## Support

For issues and questions:
- Check application logs: `docker-compose logs localmind`
- Check Ollama logs: `docker-compose logs ollama`
- Review API documentation: `http://localhost:8000/docs`
