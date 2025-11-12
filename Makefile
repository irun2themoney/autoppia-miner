.PHONY: help install test run api clean lint format

help:
	@echo "Autoppia Miner - Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run tests"
	@echo "  make run        - Run worker directly"
	@echo "  make api        - Run API server"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make lint       - Run linter"
	@echo "  make format     - Format code"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v

run:
	python worker.py

api:
	python api.py

clean:
	rm -rf __pycache__/
	rm -rf *.pyc
	rm -rf .pytest_cache/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	rm -rf logs/

lint:
	flake8 worker.py api.py utils.py --max-line-length=120 --ignore=E501,W503

format:
	black worker.py api.py utils.py tests/

