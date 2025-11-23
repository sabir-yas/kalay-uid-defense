#!/usr/bin/env python3
import requests, time, sys

EMULATOR = "http://localhost:5000"
MONITOR = "http://localhost:5001"

class SecurityController:
    def __init__(self):
        self.emulator_host = "localhost:5000"
        self.monitor_host = "localhost:5001"

    def enable_full_protection(self):
        """Enable both AuthKey AND Moving Target Defense"""
        print("🛡️  ACTIVATING FULL SECURITY SUITE...")
        print("=" * 50)
        
        # Enable AuthKey
        print("🔐 Enabling AuthKey Authentication...")
        auth_response = requests.post(f"{EMULATOR}/config", json={"authkey": True})
        time.sleep(1)
        
        # Enable MTD
        print("🎯 Enabling Moving Target Defense...")
        mtd_response = requests.post(f"{EMULATOR}/config", json={"mtd": True})
        time.sleep(1)
        
        # Generate traps
        print("🕸️  Deploying UID Decoys...")
        traps_response = requests.post(f"{EMULATOR}/mtd/generate_spoofed", json={"count": 20})
        time.sleep(1)
        
        print("=" * 50)
        print("✅ FULL SECURITY SUITE ACTIVATED!")
        print("   🔐 AuthKey - Cryptographic authentication")
        print("   🎯 MTD - Moving Target Defense with decoys")
        print("   🛡️  Layered protection enabled")
        
        return {
            "authkey": auth_response.json(),
            "mtd": mtd_response.json(),
            "traps": traps_response.json()
        }

    def disable_all_defenses(self):
        """Disable all security (vulnerable mode for demo)"""
        print("⚠️  DISABLING ALL SECURITY DEFENSES...")
        response1 = requests.post(f"{EMULATOR}/config", json={"authkey": False, "mtd": False})
        response2 = requests.post(f"{EMULATOR}/reset")
        
        print("✅ All defenses disabled - System in VULNERABLE state")
        return response1.json()

    def enable_authkey_only(self):
        """Enable only AuthKey protection"""
        print("🔐 Enabling AuthKey Protection Only...")
        response = requests.post(f"{EMULATOR}/config", json={"authkey": True, "mtd": False})
        print("✅ AuthKey protection enabled")
        return response.json()

    def enable_mtd_only(self):
        """Enable only Moving Target Defense"""
        print("🎯 Enabling MTD Protection Only...")
        response = requests.post(f"{EMULATOR}/config", json={"authkey": False, "mtd": True})
        traps_response = requests.post(f"{EMULATOR}/mtd/generate_spoofed", json={"count": 15})
        print("✅ MTD protection enabled with 15 decoys")
        return response.json()

    def get_security_status(self):
        """Get detailed security status from monitor"""
        print("\n📊 SECURITY STATUS OVERVIEW")
        print("=" * 40)
        
        try:
            # Get status from security monitor
            monitor_response = requests.get(f"{MONITOR}/api/security/status")
            stats_response = requests.get(f"{EMULATOR}/stats")
            traps_response = requests.get(f"{EMULATOR}/mtd/traps")
            
            if monitor_response.status_code == 200:
                stats = monitor_response.json()
                emulator_stats = stats_response.json() if stats_response.status_code == 200 else {}
                traps = traps_response.json() if traps_response.status_code == 200 else {}
                
                # Security status
                auth_status = "🔐 ENABLED" if stats.get('authkey_enabled', False) else "❌ DISABLED"
                mtd_status = "🎯 ENABLED" if stats.get('mtd_enabled', False) else "❌ DISABLED"
                
                print(f"AuthKey Protection:    {auth_status}")
                print(f"MTD Protection:        {mtd_status}")
                print(f"DTLS Encryption:       {'🔒 ENABLED' if stats.get('dtls_enabled', False) else '❌ DISABLED'}")
                print(f"Active Clients:        {stats.get('active_clients', 0)}")
                print(f"UID Changes Detected:  {stats.get('uid_changes_detected', 0)}")
                print(f"Auth Failures:         {stats.get('auth_failures', 0)}")
                print(f"MTD Traps Triggered:   {stats.get('mtd_changes', 0)}")
                
                if traps:
                    print(f"MTD Decoys Deployed:   {traps.get('total_traps', 0)}")
                
                # Overall security level
                auth_enabled = stats.get('authkey_enabled', False)
                mtd_enabled = stats.get('mtd_enabled', False)
                
                if auth_enabled and mtd_enabled:
                    print(f"\n🏆 SECURITY LEVEL: MAXIMUM PROTECTION")
                    print("   Both AuthKey and MTD active - Layered defense")
                elif auth_enabled:
                    print(f"\n🛡️  SECURITY LEVEL: STANDARD PROTECTION") 
                    print("   AuthKey active - Basic authentication")
                elif mtd_enabled:
                    print(f"\n🎯 SECURITY LEVEL: ACTIVE DEFENSE")
                    print("   MTD active - Attack detection and confusion")
                else:
                    print(f"\n💀 SECURITY LEVEL: VULNERABLE")
                    print("   No protections active - Attackers can compromise devices")
                
                # Show recent events
                events = stats.get('recent_events', [])
                if events:
                    print(f"\n📋 RECENT SECURITY EVENTS:")
                    for event in events[-3:]:  # Show last 3 events
                        print(f"   • {event}")
                    
            return stats
            
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to security monitor. Is it running?")
            return {}
        except Exception as e:
            print(f"❌ Error getting security status: {e}")
            return {}

    def enable_authkey(self):
        """Enable AuthKey protection"""
        response = requests.post(f"{EMULATOR}/config", json={"authkey": True})
        print("🔐 AuthKey protection enabled")
        return response.json()

    def disable_authkey(self):
        """Disable AuthKey protection"""
        response = requests.post(f"{EMULATOR}/config", json={"authkey": False})
        print("🔓 AuthKey protection disabled")
        return response.json()

    def enable_mtd(self):
        """Enable Moving Target Defense"""
        response = requests.post(f"{EMULATOR}/config", json={"mtd": True})
        traps_response = requests.post(f"{EMULATOR}/mtd/generate_spoofed", json={"count": 10})
        print("🎯 MTD enabled with 10 decoys")
        return response.json()

    def disable_mtd(self):
        """Disable Moving Target Defense"""
        response = requests.post(f"{EMULATOR}/config", json={"mtd": False})
        print("🎯 MTD protection disabled")
        return response.json()

    def generate_traps(self, count=10):
        """Generate MTD decoy UIDs"""
        response = requests.post(f"{EMULATOR}/mtd/generate_spoofed", json={"count": count})
        print(f"🕸️  Generated {count} MTD decoy UIDs")
        return response.json()

    def show_traps(self):
        """Show MTD trap status"""
        response = requests.get(f"{EMULATOR}/mtd/traps")
        if response.status_code == 200:
            traps = response.json()
            print(f"\n🎯 MTD TRAP STATUS")
            print("=" * 30)
            print(f"Total Decoys: {traps.get('total_traps', 0)}")
            print(f"Traps Triggered: {traps.get('traps_triggered', 0)}")
            print(f"Total Attack Attempts: {traps.get('total_attempts', 0)}")
            
            spoofed_uids = traps.get('spoofed_uids', [])
            if spoofed_uids:
                print(f"\nSample Decoy UIDs:")
                for uid in spoofed_uids[:5]:  # Show first 5
                    print(f"  • {uid}")
        return response.json()

    def reset_system(self):
        """Reset the entire system"""
        response = requests.post(f"{EMULATOR}/reset")
        print("🔄 System reset complete - all UIDs and traps cleared")
        return response.json()

if __name__ == "__main__":
    controller = SecurityController()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "full":
            controller.enable_full_protection()
        elif command == "vulnerable":
            controller.disable_all_defenses()
        elif command == "authkey_only":
            controller.enable_authkey_only()
        elif command == "mtd_only":
            controller.enable_mtd_only()
        elif command == "status":
            controller.get_security_status()
        elif command == "enable":
            controller.enable_authkey()
        elif command == "disable":
            controller.disable_authkey()
        elif command == "enable_mtd":
            controller.enable_mtd()
        elif command == "disable_mtd":
            controller.disable_mtd()
        elif command == "generate_traps":
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            controller.generate_traps(count)
        elif command == "traps":
            controller.show_traps()
        elif command == "reset":
            controller.reset_system()
        else:
            print("Commands: full, vulnerable, authkey_only, mtd_only, status, enable, disable, enable_mtd, disable_mtd, generate_traps, traps, reset")
    else:
        controller.get_security_status()
