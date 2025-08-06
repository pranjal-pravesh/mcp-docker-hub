.PHONY: help install setup dev test clean deploy-local deploy-railway deploy-render

help: ## Show this help message
	@echo "MCP Hub Server - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	@if [ -d "venv" ]; then \
		source venv/bin/activate && pip install -r requirements.txt; \
	else \
		pip install -r requirements.txt; \
	fi

setup: ## Initial setup (install dependencies and create .env)
	@if [ -d "venv" ]; then \
		source venv/bin/activate && pip install -r requirements.txt; \
	else \
		pip install -r requirements.txt; \
	fi
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "Created .env file. Please edit it with your API keys."; \
	else \
		echo ".env file already exists."; \
	fi

dev: ## Start development server
	@if [ -d "venv" ]; then \
		source venv/bin/activate && python run_hub.py --dev --add-all-servers; \
	else \
		python run_hub.py --dev --add-all-servers; \
	fi

test: ## Run tests
	@if [ -d "venv" ]; then \
		source venv/bin/activate && python -m pytest examples/test_mcp_hub.py --offline; \
	else \
		python -m pytest examples/test_mcp_hub.py --offline; \
	fi

test-online: ## Run online tests (requires running server)
	@if [ -d "venv" ]; then \
		source venv/bin/activate && python -m pytest examples/test_mcp_hub.py; \
	else \
		python -m pytest examples/test_mcp_hub.py; \
	fi

clean: ## Clean up Python cache files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

deploy-local: ## Deploy locally with Docker
	./deployment/deploy.sh local

deploy-railway: ## Deploy to Railway
	./deployment/deploy.sh railway

deploy-render: ## Deploy to Render
	./deployment/deploy.sh render

docker-build: ## Build Docker image
	docker build -f deployment/Dockerfile -t mcp-hub-server .

docker-run: ## Run Docker container locally
	docker run -p 8000:8000 --env-file .env mcp-hub-server

logs: ## Show Docker logs
	docker-compose -f deployment/docker-compose.yml logs -f

stop: ## Stop Docker containers
	docker-compose -f deployment/docker-compose.yml down 