echo "Starting server..."
source venv/bin/activate

# Function to handle cleanup
cleanup() {
    echo "Stopping servers..."
    kill $WEBPACK_PID $PYTHON_PID
    wait $WEBPACK_PID $PYTHON_PID 2>/dev/null
    echo "Servers stopped."
}

# Trap SIGINT (Ctrl+C) and call cleanup
trap cleanup SIGINT

# Start Webpack dev server in the background
( cd ui && npm start ) &
WEBPACK_PID=$!

# Start Python server
DASHBOARD_URL=http://localhost:4010/index.js python -m server.server --url $1 &
PYTHON_PID=$!

# Wait for both background processes to complete
wait $WEBPACK_PID $PYTHON_PID
