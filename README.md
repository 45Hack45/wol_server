# Wake-on-LAN and TrueNAS Monitoring Server

This project provides a Python-based web server for managing and monitoring devices on your network using Wake-on-LAN (WoL) and SSH. The server allows you to wake up devices, shut them down remotely, and monitor a TrueNAS server for CPU and network load, with an automatic shutdown feature and email notifications.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Server](#running-the-server)
- [Running the TrueNAS Monitor](#running-the-nas-monitor)
- [Usage](#usage)
- [Setting Up as a Systemd Service](#setting-up-as-a-systemd-service)

## Features

- **Wake-on-LAN (WoL):** Wake up devices on your network using their MAC addresses.
- **Remote Shutdown:** Remotely shut down devices via SSH.
- **Device Status Monitoring:** Check if a device is online or offline.
- **TrueNAS Monitoring:** Monitor a TrueNAS server's CPU and network load.
- **Automated Shutdown:** Automatically shut down the NAS when it detects low CPU and network activity.
- **Email Notifications:** Receive notifications via email when certain actions, like NAS shutdown, are triggered.

## Requirements

- **Python 3.8+**: The scripts require Python version 3.8 or higher.
- **Python Packages**: Several Python packages are required, including Flask and wakeonlan.

## Installation

To set up the project, follow these steps:

1. **Clone the Repository**: Start by cloning the repository to your local machine.

2. **Install Dependencies**: Install all necessary Python packages. A `requirements.txt` file is provided to facilitate this process.

3. **Prepare Configuration Files**: The project uses several JSON files for configuration:
   - `devices.json`: Lists the devices to manage and monitor.
   - `config.json`: Contains the configuration settings for the TrueNAS monitoring and email notifications.
   - `credentials.json`: Stores sensitive information like authentication credentials.

   **Note:** Example configurations will be provided, and you should modify them to suit your environment.

## Configuration

### devices.json

This file contains a list of devices that the server will manage. Each device entry includes:
- **id**: A unique identifier for the device.
- **name**: A descriptive name for the device.
- **mac**: The MAC address used for sending the WoL magic packet.
- **ip**: The IP address used to check the device's status and for SSH operations.
- **ssh_user**: The SSH username for shutting down the device.

### config.json

This file configures the TrueNAS monitoring and email notification settings. It includes:
- **url**: The base URL for the Wake-on-LAN server.
- **truenas_wol_server_id**: The ID of the TrueNAS server in the `devices.json` file.
- **shutdown_delay**: The delay before shutting down the NAS, in minutes.
- **mail_notification_sender**: The email address that sends notifications.
- **mail_notification_recipients**: A list of email addresses to receive notifications.

### credentials.json

This file stores sensitive information, such as:
- **truenas_wol_auth**: The authentication token or credentials for accessing the TrueNAS API.
- **mail_notification_password**: The password for the email account used to send notifications.

## Running the Server

To start the Flask web server:
- Run the command: `python3 wol_server.py`
- The server will start on the specified host and port, allowing you to access the web interface via a browser.

## Running the TrueNAS Monitor
Create a Cron Job to run the TrueNAS monitoring script every 30 minutes.
In linux 

```bash
```sudo crontab -e
*/30 * * * * bash path/to/script/monitoring_script.sh
```

The TrueNAS monitoring script checks the CPU and network load of the TrueNAS server and triggers a shutdown if both loads are low. It also sends an email notification with the shutdown details and a link to cancel the shutdown.

## Usage

### Web Interface

- **Dashboard**: The main page lists all configured devices, showing whether they are online or offline.
- **Wake Device**: Each device has a button to send a WoL magic packet, waking up the device.
- **Shut Down Device**: If a device is online, you can shut it down using a button on the dashboard.

### TrueNAS Monitoring

- The script continuously monitors the NAS and triggers a shutdown if low CPU and network activity are detected.
- If the NAS is scheduled for shutdown, an email notification is sent with a link to cancel the shutdown.

## Setting Up as a Systemd Service

To ensure that the Wake-on-LAN server starts automatically on boot, you can set it up as a systemd service. The provided `setup_wol_service.sh` script simplifies this process.

### setup_wol_service.sh

This Bash script creates and configures a systemd service to run the Wake-on-LAN server. Here's how it works:

1. **Variables Configuration**:
   - `USERNAME`: Your system username (default: `raspberry`).
   - `GROUPNAME`: Your system group name (default: `raspberry`).
   - `PROJECT_DIR`: The directory where your project is located (default: `/home/raspberry/wol_server`).
   - `SERVICE_NAME`: The name of the systemd service (`wol-server.service`).
   - `PYTHON_EXEC`: The path to the Python executable (default: `/usr/bin/python3`).

2. **Service File Creation**:
   - The script creates a systemd service file at `/etc/systemd/system/wol-server.service`.
   - This service file defines how the server should start, specifying the working directory, the user and group to run as, and the command to execute the server.

3. **Systemd Reload and Enable**:
   - After creating the service file, the script reloads the systemd daemon to recognize the new service.
   - The service is then enabled to start automatically on system boot.

4. **Service Start**:
   - The script starts the service immediately after enabling it.
   - Finally, it checks and displays the status of the service to confirm that it is running correctly.

### Running the Script

To set up the server as a systemd service:

```bash
```sudo bash setup_wol_service.sh
This command will execute the script, setting up and starting the Wake-on-LAN server as a service on your system.