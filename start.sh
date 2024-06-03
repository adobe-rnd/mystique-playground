echo "Starting server..."
source venv/bin/activate
python -m server.server --url $1
