#!/usr/bin/env python3
"""
Decryption utility for the ethical keylogger
Decrypts and displays the logged keystrokes

Made By Vision
GitHub: github.com/vision-dev1
Website: https://visionkc.com.np
"""

import os
import sqlite3
import json
from cryptography.fernet import Fernet
from datetime import datetime

class KeylogDecryptor:
    def __init__(self, db_path="keylogs.db", key_path="secret.key"):
        self.db_path = db_path
        self.key_path = key_path
        
        # Check if files exist
        if not os.path.exists(self.key_path):
            raise FileNotFoundError(f"Encryption key file '{self.key_path}' not found")
            
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file '{self.db_path}' not found")
            
        # Load encryption key
        with open(self.key_path, 'rb') as key_file:
            key = key_file.read()
        self.cipher_suite = Fernet(key)

    def decrypt_data(self, encrypted_data):
        """Decrypt data using Fernet"""
        try:
            decrypted = self.cipher_suite.decrypt(encrypted_data.encode()).decode()
            return decrypted
        except Exception as e:
            return f"[DECRYPTION_ERROR: {str(e)}]"

    def display_keystrokes(self, filter_date=None, filter_window=None):
        """Display decrypted keystrokes with optional filtering"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build query with filters
        query = "SELECT timestamp, window_title, key_data FROM keystrokes WHERE is_encrypted = 1"
        params = []
        
        if filter_date:
            query += " AND timestamp LIKE ?"
            params.append(f"{filter_date}%")
            
        if filter_window:
            query += " AND window_title LIKE ?"
            params.append(f"%{filter_window}%")
            
        query += " ORDER BY timestamp ASC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        print("=" * 80)
        print("DECRYPTED KEYSTROKES LOG")
        print("=" * 80)
        print(f"{'Timestamp':<25} {'Window Title':<30} {'Keystroke'}")
        print("-" * 80)
        
        for row in rows:
            timestamp, window_title, encrypted_key_data = row
            decrypted_key_data = self.decrypt_data(encrypted_key_data)
            
            # Truncate long window titles
            if len(window_title) > 28:
                window_title = window_title[:25] + "..."
                
            print(f"{timestamp:<25} {window_title:<30} {decrypted_key_data}")
            
        print("-" * 80)
        print(f"Total records: {len(rows)}")
        conn.close()

    def export_to_txt(self, filename="keylog_export.txt", filter_date=None, filter_window=None):
        """Export decrypted keystrokes to a text file"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build query with filters
        query = "SELECT timestamp, window_title, key_data FROM keystrokes WHERE is_encrypted = 1"
        params = []
        
        if filter_date:
            query += " AND timestamp LIKE ?"
            params.append(f"{filter_date}%")
            
        if filter_window:
            query += " AND window_title LIKE ?"
            params.append(f"%{filter_window}%")
            
        query += " ORDER BY timestamp ASC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        with open(filename, 'w') as f:
            f.write("DECRYPTED KEYSTROKES LOG\n")
            f.write("=" * 80 + "\n")
            f.write(f"Exported on: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n")
            f.write(f"{'Timestamp':<25} {'Window Title':<30} {'Keystroke'}\n")
            f.write("-" * 80 + "\n")
            
            for row in rows:
                timestamp, window_title, encrypted_key_data = row
                decrypted_key_data = self.decrypt_data(encrypted_key_data)
                
                # Truncate long window titles
                if len(window_title) > 28:
                    window_title = window_title[:25] + "..."
                    
                f.write(f"{timestamp:<25} {window_title:<30} {decrypted_key_data}\n")
                
            f.write("-" * 80 + "\n")
            f.write(f"Total records: {len(rows)}\n")
            
        conn.close()
        print(f"[+] Exported {len(rows)} records to {filename}")

    def export_to_csv(self, filename="keylog_export.csv", filter_date=None, filter_window=None):
        """Export decrypted keystrokes to a CSV file"""
        import csv
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build query with filters
        query = "SELECT timestamp, window_title, key_data FROM keystrokes WHERE is_encrypted = 1"
        params = []
        
        if filter_date:
            query += " AND timestamp LIKE ?"
            params.append(f"{filter_date}%")
            
        if filter_window:
            query += " AND window_title LIKE ?"
            params.append(f"%{filter_window}%")
            
        query += " ORDER BY timestamp ASC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Timestamp', 'Window Title', 'Keystroke'])
            
            for row in rows:
                timestamp, window_title, encrypted_key_data = row
                decrypted_key_data = self.decrypt_data(encrypted_key_data)
                writer.writerow([timestamp, window_title, decrypted_key_data])
                
        conn.close()
        print(f"[+] Exported {len(rows)} records to {filename}")

    def show_system_events(self):
        """Display system events"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT timestamp, event_type, event_data FROM system_events ORDER BY timestamp ASC")
        rows = cursor.fetchall()
        
        print("=" * 80)
        print("SYSTEM EVENTS LOG")
        print("=" * 80)
        print(f"{'Timestamp':<25} {'Event Type':<20} {'Event Data'}")
        print("-" * 80)
        
        for row in rows:
            timestamp, event_type, event_data = row
            print(f"{timestamp:<25} {event_type:<20} {event_data}")
            
        print("-" * 80)
        print(f"Total events: {len(rows)}")
        conn.close()

    def show_alerts(self):
        """Display security alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT timestamp, alert_type, alert_data FROM alerts ORDER BY timestamp ASC")
        rows = cursor.fetchall()
        
        print("=" * 80)
        print("SECURITY ALERTS")
        print("=" * 80)
        print(f"{'Timestamp':<25} {'Alert Type':<20} {'Alert Data'}")
        print("-" * 80)
        
        for row in rows:
            timestamp, alert_type, alert_data = row
            print(f"{timestamp:<25} {alert_type:<20} {alert_data}")
            
        print("-" * 80)
        print(f"Total alerts: {len(rows)}")
        conn.close()

def main():
    """Main function"""
    try:
        decryptor = KeylogDecryptor()
        
        while True:
            print("\n" + "="*50)
            print("KEYLOGGER DECRYPTION UTILITY")
            print("="*50)
            print("1. Display all keystrokes")
            print("2. Filter by date (YYYY-MM-DD)")
            print("3. Filter by window title")
            print("4. Export to TXT")
            print("5. Export to CSV")
            print("6. Show system events")
            print("7. Show security alerts")
            print("8. Exit")
            print("-"*50)
            
            choice = input("Select an option (1-8): ").strip()
            
            if choice == '1':
                decryptor.display_keystrokes()
            elif choice == '2':
                date_filter = input("Enter date (YYYY-MM-DD): ").strip()
                decryptor.display_keystrokes(filter_date=date_filter)
            elif choice == '3':
                window_filter = input("Enter window title keyword: ").strip()
                decryptor.display_keystrokes(filter_window=window_filter)
            elif choice == '4':
                filename = input("Enter filename (default: keylog_export.txt): ").strip()
                if not filename:
                    filename = "keylog_export.txt"
                decryptor.export_to_txt(filename)
            elif choice == '5':
                filename = input("Enter filename (default: keylog_export.csv): ").strip()
                if not filename:
                    filename = "keylog_export.csv"
                decryptor.export_to_csv(filename)
            elif choice == '6':
                decryptor.show_system_events()
            elif choice == '7':
                decryptor.show_alerts()
            elif choice == '8':
                print("[*] Exiting...")
                break
            else:
                print("[!] Invalid option. Please try again.")
                
    except FileNotFoundError as e:
        print(f"[!] Error: {e}")
        print("[!] Make sure you're running this script in the same directory as keylogger.py")
    except Exception as e:
        print(f"[!] An error occurred: {e}")

if __name__ == "__main__":
    main()