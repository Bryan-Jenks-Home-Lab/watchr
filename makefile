GREEN=\033[0;32m
NC=\033[0m # No Color
APP_NAME=$(shell poetry version | cut -d' ' -f1)
APP_VERSION=$(shell poetry version -s)
DB_CONNECTION_STRING=$(shell dotenv get DB_CONNECTION_STRING)
DEPLOYMENT_COMMAND=$(shell read choice)

app:
	@./common/version-bump.sh

format:
	isort --profile black ./src
	black ./src
run:
	poetry run python3 src/main.py
test:
	@echo "\n🧪️ ${GREEN}Running Test Suite${NC}\n"
	poetry run python3 -m pytest --verbose
	@echo "\n🧪️ ${GREEN}Cleaning Up Test Suite Artifacts${NC}\n"
	@$(MAKE) clean
	@echo "\n🧪️ ${GREEN}Test Suite Execution Completed${NC}\n"
clean:
	@echo "\n🧹️ ${GREEN}Cleaning Up${NC}\n"
	rm -rf **/.pytest_cache
	rm -rf .pytest_cache
	rm -rf **/__pycache__
	@echo "\n🧹️ ${GREEN}Cleaned${NC}\n"
build:
	@echo "\n🛠️ ${GREEN}Beginning Build Process${NC}\n"
	@if (! docker stats --no-stream ); then open /Applications/Docker.app; while (! docker stats --no-stream ); do echo "Waiting for Docker to launch..." && sleep 1; done; fi
	poetry update
	poetry export --without-hashes --format requirements.txt --output requirements.txt
	@echo "\n🛠️ ${GREEN}Attempting To Build Container${NC}\n"
	docker build -t bryan-jenks-home-lab/${APP_NAME}:${APP_VERSION} .
	@echo "\n🛠️ ${GREEN}Attempting To Run Container${NC}\n"
	docker run -d \
		-e DB_CONNECTION_STRING=${DB_CONNECTION_STRING} \
		-e EXPECTED_FILE=strong.csv \
		-e TARGET_TABLE=health.strongapp.workout_data \
		-e WATCH_PATH=/data/inbound \
		-e STAGING_PATH=/data/outbound \
		-e PROCESSED_PATH=/data/processed \
		-v /Volumes/sql/services/strong_app_import/inbound:/data/inbound \
		-v /Volumes/sql/services/strong_app_import/outbound:/data/outbound \
		-v /Volumes/sql/services/strong_app_import/processed:/data/processed \
		bryan-jenks-home-lab/${APP_NAME}:${APP_VERSION}
	@echo "\n🛠️ ${GREEN}Build Process Completed${NC}\n"
deploy:
	@echo "\n🚀️ ${GREEN}Beginning Deployment Process${NC}\n"
	
	@echo "\n🚀️ ${GREEN}Deployment Process Completed${NC}\n"