# Ethical Keylogger Installation Guide

Made By Vision  
GitHub: [github.com/vision-dev1](https://github.com/vision-dev1)  
Website: [https://visionkc.com.np](https://visionkc.com.np)

## Overview

This document provides detailed instructions for installing and setting up the Ethical Keylogger on Linux systems, specifically tested on Kali Linux.

## Prerequisites

- Linux operating system (tested on Kali Linux)
- Python 3.6 or higher
- Root privileges for some system monitoring features
- X11 display server (for window title detection)

## Dependencies

The keylogger requires the following system and Python packages:

### System Dependencies

```bash
# Install required system packages
sudo apt update
sudo apt install python3-pip xdotool scrot -y
```

### Python Dependencies

All Python dependencies are listed in [requirements.txt](requirements.txt):

- `pynput` - For capturing keyboard events
- `cryptography` - For encrypting logs
- `psutil` - For system monitoring
- `flask` - For the web dashboard

## Installation Steps

1. **Clone or Download the Repository**

   ```bash
   cd /home/vision/Desktop/
   # If you downloaded the zip, extract it to Keylogger folder
   ```

2. **Install Python Dependencies**

   ```bash
   cd Keylogger
   pip3 install -r requirements.txt
   ```

3. **Verify Installation**

   Check that all required tools are installed:
   
   ```bash
   python3 --version
   xdotool --version
   scrot --version
   ```

## Usage Instructions

### Running the Keylogger Directly

To run the keylogger directly:

```bash
# Activate the virtual environment
source venv/bin/activate

# Run the keylogger
python3 keylogger.py
```

Features:
- Press `ESC` to safely stop logging
- Press `F12` to take a screenshot (saved as screenshot_YYYYMMDD_HHMMSS_N.png)
- All logs are encrypted and stored in `keylogs.db`

### Using the Decryption Utility

To view encrypted logs:

```bash
# Activate the virtual environment
source venv/bin/activate

# Run the decryption utility
python3 decrypt.py
```

This opens an interactive menu to:
- Display all keystrokes
- Filter by date or window title
- Export to TXT or CSV formats
- View system events and security alerts

### Web Dashboard

To start the web dashboard:

```bash
# Activate the virtual environment
source venv/bin/activate

# Run the dashboard
python3 dashboard.py
```

Then open your browser to `http://127.0.0.1:5000`

Features:
- Start/stop keylogger remotely
- View decrypted logs in real-time
- Filter logs by date or window title
- Export logs to TXT or CSV
- View system statistics

### Setting up as a System Service

To install the keylogger as a systemd service:

1. Edit the service file to match your system:
   ```bash
   nano keylogger.service
   ```
   
2. Update the `User` and `Group` fields to match your username:
   ```
   User=your_username
   Group=your_group
   ```

3. Copy the service file to systemd:
   ```bash
   sudo cp keylogger.service /etc/systemd/system/
   ```

4. Reload systemd and enable the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable keylogger.service
   ```

5. Start/stop the service:
   ```bash
   sudo systemctl start keylogger.service
   sudo systemctl stop keylogger.service
   ```

6. Check service status:
   ```bash
   sudo systemctl status keylogger.service
   ```

## File Structure

```
Keylogger/
├── keylogger.py          # Main keylogger script
├── decrypt.py            # Decryption utility
├── dashboard.py          # Flask web dashboard
├── keylogger.service     # Systemd service file
├── requirements.txt      # Python dependencies
├── INSTALL.md            # This installation guide
├── keylogs.db           # Encrypted SQLite database (created on first run)
├── secret.key           # Encryption key (created on first run)
└── screenshots/         # Screenshot directory (created when needed)
```

## Security Features

1. **Encryption**: All keystrokes are encrypted using Fernet symmetric encryption
2. **Local Storage Only**: No remote transmission of data
3. **Pattern Detection**: Credit cards and email addresses are detected but not stored
4. **Password Field Detection**: Password fields are detected and not recorded
5. **System Event Logging**: USB insertion, network activity, and terminal opening are logged

## Legal and Ethical Usage

This tool is intended for:
- Personal security research
- Educational purposes
- Authorized penetration testing
- Monitoring your own systems

⚠️ **Important**: Only use this software on systems you own or have explicit permission to monitor. Unauthorized surveillance is illegal and unethical.

## Troubleshooting

### Common Issues

1. **Permission Errors**
   - Some features require root privileges
   - Run with `sudo` for full functionality

2. **X11 Display Issues**
   - Ensure you're running on an X11 session
   - Wayland sessions may have limitations

3. **Missing Dependencies**
   - Install all required system packages
   - Check Python package versions

### Logs and Debugging

- Application logs: `keylogger.log`
- Database file: `keylogs.db`
- Encryption key: `secret.key`
- Screenshots: `screenshot_YYYYMMDD_HHMMSS_N.png`

## Designed by Vision

For support and updates, visit:
- GitHub: [github.com/vision-dev1](https://github.com/vision-dev1)
- Website: [https://visionkc.com.np](https://visionkc.com.np)