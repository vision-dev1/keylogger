# Advanced Ethical Keylogger for Linux

Made By Vision  
GitHub: [github.com/vision-dev1](https://github.com/vision-dev1)  
Website: [https://visionkc.com.np](https://visionkc.com.np)

## Overview

This is a comprehensive, ethical keylogger and activity monitoring tool designed specifically for Linux systems. It captures keystrokes, monitors system events, and provides a secure web interface for management - all while respecting privacy and emphasizing legal use.

⚠️ **DISCLAIMER**: This tool is for educational and authorized security research purposes only. Only use on systems you own or have explicit permission to monitor.

## Features

### Core Functionality
- Records every keystroke with precise timestamps
- Captures active window titles using xdotool
- Clearly displays special keys (Enter, Tab, Shift, Ctrl, etc.)
- Encrypts all logs using Fernet cryptography
- Provides a separate decryption utility to view logs
- ESC key safely stops logging

### Advanced Security Features
- Local-only Flask web dashboard for management
- System information logging (CPU, RAM, username, network status)
- Intelligent password field detection (warns but doesn't capture)
- Pattern detection for sensitive data:
  - 16-digit sequences (credit cards) - alerts only
  - Email patterns - alerts only
- Manual screenshot trigger using F12 key
- Comprehensive system event logging:
  - USB device insertion
  - Network connectivity changes
  - Terminal application launches

### Data Management
- Stores all logs in an encrypted SQLite database
- Exports logs to TXT or CSV formats
- Systemd service file for easy start/stop management
- Clean, modular, and secure codebase

## Test Images

![image alt](test-keylogger1.png](https://github.com/vision-dev1/keylogger/blob/be64f85b061adcf90349d5f68be8ebf3de244d88/keylogger-test1.png)

![Test Keylogger 2](test-keylogger2.png)

## Running the Keylogger

### Method 1: Using Startup Scripts (Recommended)
```bash
# Start the keylogger
./start_keylogger.sh

# View decrypted logs
./view_logs.sh

# Start the web dashboard
./start_dashboard.sh
```

### Method 2: Direct Python Execution
```bash
# Activate virtual environment
source venv/bin/activate

# Run the keylogger
python3 keylogger.py

# View decrypted logs
python3 decrypt.py

# Start the web dashboard
python3 dashboard.py
```

Controls while running:
- Press `ESC` to safely stop logging
- Press `F12` to take a screenshot

## File Structure

```
Keylogger/
├── keylogger.py          # Main keylogger script
├── decrypt.py            # Decryption utility
├── dashboard.py          # Flask web dashboard
├── keylogger.service     # Systemd service file
├── requirements.txt      # Python dependencies
├── INSTALL.md            # Detailed installation guide
├── README.md             # This file
├── keylogs.db           # Encrypted SQLite database (created on first run)
├── secret.key           # Encryption key (created on first run)
└── screenshots/         # Screenshot directory (created when needed)
```

## Installation

Detailed installation instructions can be found in [INSTALL.md](INSTALL.md).

### Quick Start

1. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install python3-pip xdotool scrot -y
   pip3 install -r requirements.txt
   ```

2. Run the keylogger:
   ```bash
   python3 keylogger.py
   ```

3. View decrypted logs:
   ```bash
   python3 decrypt.py
   ```

4. Start the web dashboard:
   ```bash
   python3 dashboard.py
   ```
   Then visit `http://127.0.0.1:5000` in your browser.

## Legal and Ethical Usage

This tool is designed with strong ethical considerations:
- Only performs local logging (no remote transmission)
- Encrypts all stored data
- Detects but does not store sensitive patterns
- Provides clear warnings for password fields
- Includes transparent user controls

⚠️ **Remember**: Unauthorized surveillance is illegal. Only use this software on systems you own or have explicit written permission to monitor.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/vision-dev1).

---

**Designed by Vision**  
Visit [https://visionkc.com.np](https://visionkc.com.np) for more projects.
