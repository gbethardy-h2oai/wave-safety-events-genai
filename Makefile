setup: ## Install dependencies
	python3 -m venv venv
	./venv/bin/python -m pip install --upgrade pip
	./venv/bin/python -m pip install -r requirements.txt

.PHONY: run
    run export H2OGPTE_ADDRESS = ***
    run export H2OGPTE_API_KEY = ***
    run export COLLECTION_NAME = ***

run: ## Run the app with active reload and no server logs
	#H2O_WAVE_NO_LOG=True ./venv/bin/wave run src/app.py
	./venv/bin/wave run src/app.py

.PHONY: format
format:
	./venv/bin/isort .
	./venv/bin/black --exclude venv .

help: ## List all make tasks
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
