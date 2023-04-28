GREEN=\033[0;32m
NC=\033[0m # No Color
APP_NAME=strong_app_import
setup:
	poetry init
	poetry shell
install:
	pip install --upgrade pip
	pip install -r requirements.txt
format:
	isort --profile black ./src
	black ./src
run:
	python3 src/main.py
build:
	@echo "\n🛠️ ${GREEN}=============== Beginning Build Process ===============${NC} 🛠️\n"
	@if (! docker stats --no-stream ); then open /Applications/Docker.app; while (! docker stats --no-stream ); do echo "Waiting for Docker to launch..." && sleep 1; done; fi
	poetry update
	poetry export --without-hashes --format requirements.txt --output requirements.txt
	docker build -t tallguyjenks/${APP_NAME}:latest .
deploy:
	@$(MAKE) build
	docker push tallguyjenks/${APP_NAME}:latest
test:
	@echo "\n🧪️ ${GREEN}=============== Running Test Suite ===============${NC} 🧪️\n"
	python3 -m pytest --verbose
	@$(MAKE) clean
clean:
	@echo "\n🧹️ ${GREEN}=============== Cleaning Up ===============${NC} 🧹️\n"
	rm -rf **/.pytest_cache
	rm -rf .pytest_cache
	rm -rf **/__pycache__