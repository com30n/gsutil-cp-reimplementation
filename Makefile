fmt:
	isort . || true
	poetry run black . || true
	autoflake -r -i --remove-all-unused-imports --ignore-init-module-imports . || true
	flake8 . || true
	mypy . || true
