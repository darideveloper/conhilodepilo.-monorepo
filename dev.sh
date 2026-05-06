#!/bin/bash

SESSION_NAME="conhilorepilo_dev"

# Check if session exists
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "Session $SESSION_NAME already exists. Attaching..."
    tmux attach -t $SESSION_NAME
    exit 0
fi

echo "Creating new dev session: $SESSION_NAME"
# Create the session and the first window for dashboard
tmux new-session -d -s $SESSION_NAME -n 'dashboard' -c "$PWD/dashboard" 'source venv/bin/activate && portless dashboard.conhilodepilo --app-port 8000 -- python manage.py runserver'

# Create a window for the booking frontend
tmux new-window -n 'booking' -c "$PWD/booking" 'npm run dev'

# Create a window for the landing frontend
tmux new-window -n 'landing' -c "$PWD/landing" 'npm run dev'

# Set focus to the first window (dashboard)
tmux select-window -t $SESSION_NAME:0

echo "Session created. You can attach to it using: tmux attach -t $SESSION_NAME"
# tmux attach -t $SESSION_NAME
