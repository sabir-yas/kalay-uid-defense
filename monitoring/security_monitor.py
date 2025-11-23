#!/usr/bin/env python3
import requests, time, json
from datetime import datetime
from flask import Flask, jsonify

EMULATOR = "http://localhost:5000"
MONITOR_PORT = 5001

app = Flask(__name__)

# Security monitoring state
suspicious_activities = []
previous_owners = {}
security_metrics = {
    'uid_changes_detected': 0,
    'auth_failures': 0,
    'mtd_traps_triggered': 0,
    'recent_events': []
}

class SecurityMonitor:
    def __init__(self):
        self.monitoring_active = True

    def check_anomalies(self):
        """Check for suspicious registration patterns"""
        try:
            # Get current device registrations
            r = requests.get(f"{EMULATOR}/uids")
            if r.status_code != 200:
                print("[-] Cannot access /uids endpoint")
                return
                
            devices = r.json()
            
            print(f"\n--- Security Monitor [{datetime.now().strftime('%H:%M:%S')}] ---")
            print(f"Registered Devices: {len(devices)}")
            
            # Check for owner changes
            for uid, data in devices.items():
                current_owner = data.get('owner', 'unknown')
                
                # Detect owner change
                if uid in previous_owners and previous_owners[uid] != current_owner:
                    alert = f"🚨 ALERT: UID {uid} changed owner from {previous_owners[uid]} to {current_owner}"
                    event = {
                        'timestamp': datetime.now().isoformat(),
                        'alert': alert,
                        'uid': uid,
                        'old_owner': previous_owners[uid],
                        'new_owner': current_owner,
                        'type': 'owner_change'
                    }
                    suspicious_activities.append(event)
                    security_metrics['recent_events'].append(alert)
                    security_metrics['uid_changes_detected'] += 1
                    print(alert)
                
                previous_owners[uid] = current_owner
            
            # Show current device status
            for uid, data in devices.items():
                owner = data.get('owner', 'unknown')
                ip = data.get('ip', 'unknown')
                status = "⚠️ COMPROMISED" if owner == "attacker" else "✅ LEGITIMATE"
                print(f"{status} UID: {uid}, Owner: {owner}, IP: {ip}")
            
            # Show recent alerts
            if suspicious_activities:
                print(f"\n📈 Recent Alerts ({len(suspicious_activities)} total):")
                for alert in suspicious_activities[-3:]:  # Show last 3 alerts
                    print(f"   {alert['timestamp']}: {alert['alert']}")
                    
            # Keep only last 20 events
            security_metrics['recent_events'] = security_metrics['recent_events'][-20:]
                    
        except requests.exceptions.ConnectionError:
            print("[-] Cannot connect to emulator - is it running?")
        except json.JSONDecodeError:
            print("[-] Invalid response from emulator")
        except Exception as e:
            print(f"[-] Monitor error: {e}")

    def continuous_monitor(self):
        print("🛡️  Kalay Security Monitor Started")
        print("Monitoring for UID impersonation attacks...")
        print("Press Ctrl+C to stop monitoring\n")
        
        try:
            while self.monitoring_active:
                self.check_anomalies()
                time.sleep(3)  # Check every 3 seconds
        except KeyboardInterrupt:
            print("\n🛑 Security Monitor stopped")

# Flask API endpoints for security controller
@app.route('/api/security/status')
def security_status():
    """Get current security status for the controller"""
    try:
        # Get stats from emulator
        stats_response = requests.get(f"{EMULATOR}/stats")
        traps_response = requests.get(f"{EMULATOR}/mtd/traps")
        
        stats = stats_response.json() if stats_response.status_code == 200 else {}
        traps = traps_response.json() if traps_response.status_code == 200 else {}
        
        return jsonify({
            'authkey_enabled': stats.get('authkey_enabled', False),
            'mtd_enabled': stats.get('mtd_enabled', False),
            'dtls_enabled': stats.get('dtls_enabled', False),  # Will be False since not implemented
            'active_clients': stats.get('total_devices', 0),
            'uid_changes_detected': security_metrics['uid_changes_detected'],
            'auth_failures': security_metrics['auth_failures'],
            'mtd_changes': traps.get('traps_triggered', 0),
            'recent_events': security_metrics['recent_events'][-5:]  # Last 5 events
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/security/events')
def security_events():
    """Get recent security events"""
    return jsonify({
        'suspicious_activities': suspicious_activities[-10:],
        'total_alerts': len(suspicious_activities)
    })

def run_monitor_server():
    """Run the Flask API server for security controller"""
    print(f"🚀 Starting Security Monitor API on port {MONITOR_PORT}")
    app.run(host="0.0.0.0", port=MONITOR_PORT, debug=False)

if __name__ == "__main__":
    # Start the Flask API server in a separate thread
    import threading
    server_thread = threading.Thread(target=run_monitor_server, daemon=True)
    server_thread.start()
    
    # Start continuous monitoring
    monitor = SecurityMonitor()
    monitor.continuous_monitor()
