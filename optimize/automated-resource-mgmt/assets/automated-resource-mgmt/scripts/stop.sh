#!/bin/bash

# IBM Turbonomic Dashboard - Stop Script
# This script stops the running Turbonomic Dashboard application

echo "=========================================="
echo "IBM Turbonomic Dashboard - Stopping..."
echo "=========================================="

# Find and kill Python processes running app.py
PIDS=$(pgrep -f "python.*app.py")

if [ -z "$PIDS" ]; then
    echo "ℹ️  No running Turbonomic Dashboard found"
    exit 0
fi

echo "Found running processes: $PIDS"
echo ""

# Kill the processes
for PID in $PIDS; do
    echo "Stopping process $PID..."
    kill $PID 2>/dev/null
    
    # Wait a moment and check if it's still running
    sleep 1
    if ps -p $PID > /dev/null 2>&1; then
        echo "Process $PID didn't stop gracefully, forcing..."
        kill -9 $PID 2>/dev/null
    fi
done

echo ""
echo "✓ Turbonomic Dashboard stopped successfully"
