#!/usr/bin/env python3
import requests, time, json
from datetime import datetime

EMULATOR = "http://localhost:5000"

class SecurityMonitor:
    def __init__(self):
        self.suspicious_activities = []
        self.previous_owners = {}  # Track owner changes
    
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
                if uid in self.previous_owners and self.previous_owners[uid] != current_owner:
                    alert = f"🚨 ALERT: UID {uid} changed owner from {self.previous_owners[uid]} to {current_owner}"
                    self.suspicious_activities.append({
                        'timestamp': datetime.now().isoformat(),
                        'alert': alert,
                        'uid': uid,
                        'old_owner': self.previous_owners[uid],
                        'new_owner': current_owner
                    })
                    print(alert)
                
                self.previous_owners[uid] = current_owner
            
            # Show current device status
            for uid, data in devices.items():
                owner = data.get('owner', 'unknown')
                ip = data.get('ip', 'unknown')
                status = "⚠️ COMPROMISED" if owner == "attacker" else "✅ LEGITIMATE"
                print(f"{status} UID: {uid}, Owner: {owner}, IP: {ip}")
            
            # Show recent alerts
            if self.suspicious_activities:
                print(f"\n📈 Recent Alerts ({len(self.suspicious_activities)} total):")
                for alert in self.suspicious_activities[-3:]:  # Show last 3 alerts
                    print(f"   {alert['timestamp']}: {alert['alert']}")
                    
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
            while True:
                self.check_anomalies()
                time.sleep(3)  # Check every 3 seconds
        except KeyboardInterrupt:
            print("\n🛑 Security Monitor stopped")

if __name__ == "__main__":
    monitor = SecurityMonitor()
    monitor.continuous_monitor()
