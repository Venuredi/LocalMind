.PHONY: help build up down restart logs clean install-phi3 health test

# Default target
help:
	@echo "LocalMind Docker Commands:"
	@echo "  make build        - Build Docker images"
	@echo "  make up           - Start all services"
	@echo "  make down         - Stop all services"
	@echo "  make restart      - Restart all services"
	@echo "  make logs         - View logs (all services)"
	@echo "  make logs-app     - View LocalMind application logs"
	@echo "  make logs-ollama  - View Ollama service logs"
	@echo "  make install-phi3 - Install Phi3 model in Ollama"
	@echo "  make health       - Check service health"
	@echo "  make clean        - Remove containers and networks"
	@echo "  make clean-all    - Remove everything including volumes"
	@echo "  make shell        - Open shell in LocalMind container"
	@echo "  make test         - Run tests"

# Build Docker images
build:
	docker-compose build

# Start services
up:
	docker-compose up -d
	@echo "Services started. Access LocalMind at http://localhost:8000"

# Stop services
down:
	docker-compose down

# Restart services
restart:
	docker-compose restart

# View logs
logs:
	docker-compose logs -f

logs-app:
	docker-compose logs -f localmind

logs-ollama:
	docker-compose logs -f ollama

# Install Phi3 model
install-phi3:
	@echo "Installing Phi3 model (this may take a few minutes)..."
	docker exec -it localmind-ollama ollama pull phi3:mini
	@echo "Phi3 model installed successfully!"

# Check health
health:
	@echo "Checking LocalMind health..."
	@curl -s http://localhost:8000/api/health | python3 -m json.tool || echo "LocalMind is not responding"
	@echo "\nChecking Ollama models..."
	@curl -s http://localhost:11434/api/tags | python3 -m json.tool || echo "Ollama is not responding"

# Clean up
clean:
	docker-compose down
	@echo "Containers and networks removed"

clean-all:
	docker-compose down -v
	@echo "Everything removed (including volumes)"

# Open shell in container
shell:
	docker exec -it localmind-app /bin/bash

# Run tests (if applicable)
test:
	docker exec -it localmind-app pytest

# Quick start (build, up, install model)
quickstart: build up
	@echo "Waiting for services to start..."
	@sleep 10
	@make install-phi3
	@echo "\nQuick start complete! Access LocalMind at http://localhost:8000"
