#!/bin/bash

PORT=4003
URL="http://localhost:4010"

# Function to check if the port is in use and kill the process if it is
check_and_kill_port() {
    echo "Checking if port $PORT is in use..."
    PID=$(lsof -ti:$PORT)
    if [ -n "$PID" ]; then
        echo "Port $PORT is in use by PID $PID. Killing the process..."
        kill -9 $PID
        echo "Process $PID killed."
    else
        echo "Port $PORT is free."
    fi
}

# Function to handle cleanup
cleanup() {
    echo "Stopping servers gracefully..."
    kill $SERVER_PID $WEBPACK_PID 2>/dev/null
    # Wait for up to 5 seconds for the processes to stop
    for i in {1..5}; do
        if ps -p $SERVER_PID > /dev/null || ps -p $WEBPACK_PID > /dev/null; then
            echo "Waiting for servers to stop... ($i)"
            sleep 1
        else
            echo "Servers stopped gracefully."
            return
        fi
    done
    echo "Servers did not stop in time. Forcibly killing..."
    kill -9 $SERVER_PID $WEBPACK_PID 2>/dev/null
    wait $SERVER_PID $WEBPACK_PID 2>/dev/null
    echo "Servers stopped forcibly."
}

# Trap SIGINT (Ctrl+C) and call cleanup
trap cleanup SIGINT

# Check and kill the process using the port if necessary
check_and_kill_port

echo "Starting servers..."
source venv/bin/activate

# Start Webpack dev server in the background
( cd ui && npm start ) &
WEBPACK_PID=$!

# Start the server in the background
python -m server.start_web_creator_server &
SERVER_PID=$!

# Function to check if the server is running on port 4003
check_server_running() {
    while true; do
        if lsof -ti:$PORT > /dev/null; then
            echo
            echo "Server on port $PORT is running. Opening $URL"
            open $URL
            break
        else
            echo "Waiting for server on port $PORT to start..."
            sleep 2
        fi
    done
}

# Check if the server is running and open the URL
check_server_running &

# Wait for the background processes to complete
wait $SERVER_PID $WEBPACK_PID
