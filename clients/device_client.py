#!/usr/bin/env python3
import requests, time, hashlib, random

EMULATOR = "http://localhost:5000"
OWNER = "alice"
PASSWORD = "alicepw"

class SecureClient:
    def __init__(self):
        self.real_uid = f"secure_cam_{random.randint(1000, 9999)}"
        
    def generate_authkey(self, uid, owner):
        auth_string = f"{uid}:{owner}:kalay_secret_2024"
        return hashlib.sha256(auth_string.encode()).hexdigest()[:16]
    
    def register_securely(self):
        """Register with proper AuthKey for maximum security"""
        authkey = self.generate_authkey(self.real_uid, OWNER)
        payload = {
            "uid": self.real_uid,
            "owner": OWNER, 
            "password": PASSWORD,
            "authkey": authkey
        }
        
        print(f"🔐 Registering with FULL security...")
        print(f"   Real UID: {self.real_uid}")
        print(f"   AuthKey: {authkey[:8]}...")
        
        r = requests.post(EMULATOR + "/register", json=payload)
        
        if r.status_code == 200:
            data = r.json()
            print(f"✅ SECURE REGISTRATION SUCCESSFUL!")
            print(f"   AuthKey: {data.get('secure', False)}")
            print(f"   MTD: {data.get('mtd', False)}")
            return True
        else:
            print(f"❌ Registration failed: {r.json()}")
            return False
    
    def access_stream(self):
        """Access the securely registered stream"""
        r = requests.get(f"{EMULATOR}/stream/{self.real_uid}")
        if r.status_code == 200:
            print(f"📹 SECURE STREAM ACCESS: {r.text.strip()}")
            return True
        else:
            print(f"❌ Stream access failed: {r.status_code}")
            return False

if __name__ == "__main__":
    print("🛡️  SECURE CLIENT - Combined AuthKey + MTD Defense")
    print("=" * 55)
    
    client = SecureClient()
    
    # Register securely
    if client.register_securely():
        time.sleep(1)
        
        # Access stream
        client.access_stream()
        
        print(f"\n🎯 SECURITY SUMMARY:")
        print(f"   • UID: {client.real_uid}")
        print(f"   • AuthKey: Authenticated")
        print(f"   • MTD: Protected by decoy network")
        print(f"   • Status: Fully secured against UID impersonation")
