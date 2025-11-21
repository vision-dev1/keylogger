# Ethical Keylogger Project Summary

Made By Vision  
GitHub: [github.com/vision-dev1](https://github.com/vision-dev1)  
Website: [https://visionkc.com.np](https://visionkc.com.np)

## Project Overview

This is a comprehensive, ethical keylogger and activity monitoring tool designed specifically for Linux systems. It captures keystrokes, monitors system events, and provides a secure web interface for management - all while respecting privacy and emphasizing legal use.

## Components Created

### 1. Main Keylogger (`keylogger.py`)
- Records every keystroke with precise timestamps
- Captures active window titles using xdotool
- Clearly displays special keys (Enter, Tab, Shift, Ctrl, etc.)
- Encrypts all logs using Fernet cryptography
- ESC key safely stops logging
- F12 key triggers screenshots
- Password field detection (warns but doesn't capture)
- Pattern detection for credit cards and emails (alerts only)
- System event logging (USB, network, terminal)
- Stores all data in encrypted SQLite database

### 2. Decryption Utility (`decrypt.py`)
- Decrypts and displays logged keystrokes
- Interactive menu for filtering and exporting
- Export to TXT or CSV formats
- View system events and security alerts

### 3. Web Dashboard (`dashboard.py`)
- Flask-based web interface
- Start/stop keylogger remotely
- View decrypted logs in real-time
- Filter logs by date or window title
- Export logs to TXT or CSV
- View system statistics

### 4. Systemd Service (`keylogger.service`)
- Service file for easy start/stop
- Runs at system startup
- Managed through systemctl

### 5. Supporting Files
- `requirements.txt` - Python dependencies
- `INSTALL.md` - Detailed installation guide
- `README.md` - Project overview
- `start_keylogger.sh` - Easy startup script
- `start_dashboard.sh` - Dashboard startup script
- `view_logs.sh` - Log viewing script

## Security Features

1. **Encryption**: All keystrokes encrypted with Fernet
2. **Local Storage**: No remote data transmission
3. **Pattern Detection**: Sensitive data detected but not stored
4. **Password Protection**: Password fields detected and not recorded
5. **System Monitoring**: Comprehensive event logging

## Legal and Ethical Usage

This tool is designed with strong ethical considerations:
- Only performs local logging (no remote transmission)
- Encrypts all stored data
- Detects but does not store sensitive patterns
- Provides clear warnings for password fields
- Includes transparent user controls

⚠️ **Disclaimer**: Unauthorized surveillance is illegal. Only use this software on systems you own or have explicit written permission to monitor.

## Installation

1. Install system dependencies:
   ```bash
   sudo apt update
   sudo apt install python3-pip xdotool scrot -y
   ```

2. Create virtual environment and install Python dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Run the keylogger:
   ```bash
   ./start_keylogger.sh
   ```

4. View the dashboard:
   ```bash
   ./start_dashboard.sh
   ```
   Then visit `http://127.0.0.1:5000`

## File Structure

```
Keylogger/
├── keylogger.py          # Main keylogger script
├── decrypt.py            # Decryption utility
├── dashboard.py          # Flask web dashboard
├── keylogger.service     # Systemd service file
├── requirements.txt      # Python dependencies
├── INSTALL.md            # Detailed installation guide
├── README.md             # Project overview
├── SUMMARY.md            # This file
├── start_keylogger.sh    # Keylogger startup script
├── start_dashboard.sh    # Dashboard startup script
├── view_logs.sh          # Log viewing script
├── keylogs.db           # Encrypted SQLite database
├── secret.key           # Encryption key
└── venv/                # Python virtual environment
```

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/vision-dev1).

---

**Designed by Vision**  
Visit [https://visionkc.com.np](https://visionkc.com.np) for more projects.