.PHONY: setup test lint format api frontend train evaluate

setup:
	@echo "Setting up DELPHI environment..."
	pip install -e .[dev]

test:
	@echo "Running tests..."
	pytest tests/

lint:
	@echo "Running linting..."
	flake8 src/ tests/
	mypy src/

format:
	@echo "Formatting code..."
	black src/ tests/

api:
	@echo "Starting FastAPI server..."
	uvicorn delphi.api.main:app --reload

frontend:
	@echo "Not implemented yet. Will start React frontend."

train:
	@echo "Not implemented yet. Training pipeline requires models to be built."

evaluate:
	@echo "Not implemented yet. Evaluation pipeline requires trained models."
