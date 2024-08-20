#!/bin/bash

# Start a local server to preview the reference page
cd server/generation_recipes/components || exit

# Run the Python server in the background and capture the process ID (PID)
python -m http.server 8000 &

# Store the process ID
SERVER_PID=$!

# Wait for a moment to ensure the server has started
sleep 2

# Open the browser
open http://localhost:8000/index.html

# Trap the script to detect Ctrl + C and stop the server
trap "echo 'Stopping server...'; kill $SERVER_PID; exit" INT

# Wait until the server is stopped
wait $SERVER_PID
