#!/usr/bin/env python3
import requests, time, sys

EMULATOR = "http://localhost:5000"

class SecurityController:
    def enable_authkey(self):
        """Enable AuthKey protection"""
        print("🛡️  Enabling AuthKey protection...")
        response = requests.post(f"{EMULATOR}/config", json={"authkey": True})
        if response.status_code == 200:
            print("✅ AuthKey protection ENABLED")
            print(f"   Message: {response.json()['message']}")
        else:
            print("❌ Failed to enable AuthKey")
        return response.json()

    def disable_authkey(self):
        """Disable AuthKey protection (vulnerable mode)"""
        print("⚠️  Disabling AuthKey protection...")
        response = requests.post(f"{EMULATOR}/config", json={"authkey": False})
        if response.status_code == 200:
            print("✅ AuthKey protection DISABLED")
            print(f"   Message: {response.json()['message']}")
        else:
            print("❌ Failed to disable AuthKey")
        return response.json()

    def get_status(self):
        """Get current security status"""
        response = requests.get(f"{EMULATOR}/stats")
        if response.status_code == 200:
            stats = response.json()
            print("\n📊 Security Status:")
            print(f"   AuthKey Protection: {'🔐 ENABLED' if stats['authkey_enabled'] else '⚠️ DISABLED'}")
            print(f"   Total Devices: {stats['total_devices']}")
            print(f"   Secure Devices: {stats['secure_devices']}")
            print(f"   Insecure Devices: {stats['insecure_devices']}")
            print(f"   Overall Status: {stats['security_status'].upper()}")
        return response.json()

    def reset_system(self):
        """Reset the entire system"""
        print("🔄 Resetting system...")
        response = requests.post(f"{EMULATOR}/reset")
        if response.status_code == 200:
            print("✅ System reset complete")
        return response.json()

if __name__ == "__main__":
    controller = SecurityController()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "enable":
            controller.enable_authkey()
        elif command == "disable":
            controller.disable_authkey()
        elif command == "status":
            controller.get_status()
        elif command == "reset":
            controller.reset_system()
        else:
            print("Usage: python3 security_controller.py [enable|disable|status|reset]")
    else:
        # Interactive mode
        controller.get_status()
        print("\nCommands: enable, disable, status, reset")
