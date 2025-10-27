# Justfile for TTB Label App

# Setup all dependencies
setup:
    ./setup.sh

# Run backend locally
run-backend:
    cd backend && uv run uvicorn main:app --reload

# Run frontend locally
run-frontend:
    cd frontend && npm run dev

# Run both locally in parallel
run-all:
    just run-backend & just run-frontend

# Generate test data
generate-test-data:
    cd test-data && uv run python scripts/generate_labels.py --config config/test_cases.yaml --templates templates --output output

# Test API against local server
test-api-local IMAGE:
    cd backend && API_URL="http://localhost:8000/api/verify" ./test_api.sh "../{{IMAGE}}"

# Test API against deployed server
test-api-deployed IMAGE:
    cd backend && API_URL="https://nfthomas-ttb-label-app-api.onrender.com/api/verify" ./test_api.sh "../{{IMAGE}}"

# Lint all code
lint:
    cd frontend && npm run lint
    cd backend && uv run ruff check . --fix
    cd test-data && uv run ruff check . --fix

# Format all code
format:
    cd frontend && npm run format
    cd backend && uv run ruff format .
    cd test-data && uv run ruff format .