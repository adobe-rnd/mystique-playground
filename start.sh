#!/bin/bash

echo "Starting servers..."
source venv/bin/activate

# Function to handle cleanup
cleanup() {
    echo "Stopping servers..."
    kill $WEBPACK_PID $PLAYGROUND_PID $COPILOT_PID 2>/dev/null
    wait $WEBPACK_PID $PLAYGROUND_PID $COPILOT_PID 2>/dev/null
    echo "Servers stopped."
}

  # Trap SIGINT (Ctrl+C) and call cleanup
trap cleanup SIGINT

# Start Webpack dev server in the background
( cd ui && npm start ) &
WEBPACK_PID=$!

# Start PlaygroundServer if URL is provided
if [ -n "$1" ]; then
    python -m server.start_playground_server --url "$1" &
    PLAYGROUND_PID=$!

    sleep 2

    # Generate a random value
    RANDOM_VALUE=$(openssl rand -hex 6)

    # Construct the URL
    URL="http://localhost:4000?t=$RANDOM_VALUE"

    # Open the URL in the default web browser
    open $URL
fi

# Start CopilotServer
python -m server.start_copilot_server &
COPILOT_PID=$!

# Wait for all background processes to complete
if [ -n "$PLAYGROUND_PID" ]; then
    wait $WEBPACK_PID $PLAYGROUND_PID $COPILOT_PID
else
    wait $WEBPACK_PID $COPILOT_PID
fi
