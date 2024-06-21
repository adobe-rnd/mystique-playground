#!/bin/bash

echo "Starting servers..."
source venv/bin/activate

# Function to handle cleanup
cleanup() {
    echo "Stopping servers..."
    kill $WEBPACK_PID $TOOLBOX_PID $ASSISTANT_PID 2>/dev/null
    wait $WEBPACK_PID $TOOLBOX_PID $ASSISTANT_PID 2>/dev/null
    echo "Servers stopped."
}

# Trap SIGINT (Ctrl+C) and call cleanup
trap cleanup SIGINT

# Start Webpack dev server in the background
( cd ui && npm start ) &
WEBPACK_PID=$!

# Start ToolboxServer if URL is provided
if [ -n "$1" ]; then
    python -m server.start_toolbox_server --url "$1" &
    TOOLBOX_PID=$!
fi

# Start AssistantServer
python -m server.start_assistant_server &
ASSISTANT_PID=$!

# Wait for all background processes to complete
if [ -n "$TOOLBOX_PID" ]; then
    wait $WEBPACK_PID $TOOLBOX_PID $ASSISTANT_PID
else
    wait $WEBPACK_PID $ASSISTANT_PID
fi
