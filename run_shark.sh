#!/bin/bash

# Shark ERP Process Manager
# Kills existing processes and starts fresh session

echo "🦈 Starting Shark ERP System..."

# Kill existing processes
echo "Killing existing processes..."
pkill -f "python.*bot/main.py" 2>/dev/null
pkill -f "python.*openstack/server.py" 2>/dev/null
pkill -f "tor" 2>/dev/null

# Wait for processes to terminate
sleep 3

# Check for zombie processes
echo "Checking for zombie processes..."
ps aux | grep -E "(bot|openstack|tor)" | grep -v grep | grep -v "run_shark.sh"

# Clear log files
echo "Clearing old logs..."
> logs/app.log 2>/dev/null
> logs/openstack_operations.log 2>/dev/null

# Start Tor service
echo "Starting Tor service..."
sudo systemctl start tor 2>/dev/null || service tor start 2>/dev/null
sleep 2

# Start OpenStack server
echo "Starting OpenStack server..."
python3 openstack/server.py &
OPENSTACK_PID=$!
echo "OpenStack PID: $OPENSTACK_PID"
sleep 5

# Start Telegram bot
echo "Starting Telegram bot..."
python3 bot/main.py &
BOT_PID=$!
echo "Bot PID: $BOT_PID"

# Monitor processes
echo ""
echo "System started successfully!"
echo "OpenStack: http://127.0.0.1:8080"
echo "Bot: @Shark_ERP_Bot"
echo ""
echo "Press Ctrl+C to stop all services"

# Trap Ctrl+C for clean shutdown
trap 'echo "Shutting down..."; kill $OPENSTACK_PID $BOT_PID 2>/dev/null; exit' INT

# Keep script running
while true; do
    sleep 60
done