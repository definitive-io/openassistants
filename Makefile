publish: publish-openassistants publish-openassistants-fastapi publish-openassistants-react
	@echo "All packages published!"

publish-openassistants:
	@echo "Publishing openassistants to PyPI..."
	@cd packages/openassistants && poetry publish --build

publish-openassistants-fastapi:
	@echo "Publishing openassistants-fastapi to PyPI..."
	@cd packages/openassistants-fastapi && poetry publish --build

publish-openassistants-react:
	@echo "Publishing openassistants-react to npm..."
	@cd packages/openassistants-react && npm publish

refresh-poetry:
	@echo "Refreshing Poetry environment..."
	@cd examples/fast-api-server && poetry install

run:
	@echo "Running all services..."
	@$(MAKE) run-backend &
	@$(MAKE) run-frontend &
	@while :; do sleep 1; done

run-backend:
	@echo "Running FastAPI server..."
	@cd examples/fast-api-server && poetry run ./run.sh

run-frontend:
	@echo "Running Next.js frontend..."
	@cd examples/next && yarn dev
