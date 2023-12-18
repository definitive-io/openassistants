publish: publish-openassistants publish-openassistants-fastapi publish-openassistants-ui
	@echo "All packages published!"

publish-openassistants:
	@echo "Publishing openassistants to PyPI..."
	@cd packages/openassistants && poetry publish --build

publish-openassistants-fastapi:
	@echo "Publishing openassistants-fastapi to PyPI..."
	@cd packages/openassistants-fastapi && poetry publish --build

publish-openassistants-ui:
	@echo "Publishing openassistants-ui to npm..."
	@cd packages/openassistants-ui && npm publish

refresh-poetry:
	@echo "Refreshing Poetry environment..."
	@cd examples/fast-api-server && poetry install

run:
	@echo "Running services in background..."
	@(cd examples/fast-api-server && poetry run ./run.sh) &
	@(cd examples/next && yarn dev) &
	@while :; do sleep 1; done
