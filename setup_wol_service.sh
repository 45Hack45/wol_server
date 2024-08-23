#!/bin/bash

# Variables
USERNAME="raspberry"      # Replace with your username
GROUPNAME="raspberry"     # Replace with your group name
PROJECT_DIR="/home/raspberry/wol_server"  # Replace with the path to your project
SERVICE_NAME="wol-server.service"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"
PYTHON_EXEC="/usr/bin/python3"  # Adjust if your Python executable is in a different location

# Create the service file
echo "Creating systemd service file..."

cat <<EOL | sudo tee $SERVICE_FILE > /dev/null
[Unit]
Description=Wake-on-LAN Flask Server
After=network.target

[Service]
User=$USERNAME
Group=$GROUPNAME
WorkingDirectory=$PROJECT_DIR
ExecStart=$PYTHON_EXEC $PROJECT_DIR/wol_server.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd daemon
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable the service to start on boot
echo "Enabling $SERVICE_NAME to start on boot..."
sudo systemctl enable $SERVICE_NAME

# Start the service immediately
echo "Starting $SERVICE_NAME..."
sudo systemctl start $SERVICE_NAME

# Check the status of the service
echo "Checking status of $SERVICE_NAME..."
sudo systemctl status $SERVICE_NAME

echo "Setup complete!"
