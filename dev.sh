echo "Starting server..."
source venv/bin/activate
DASHBOARD_URL=http://localhost:8080/index.js python -m server.server --url $1
