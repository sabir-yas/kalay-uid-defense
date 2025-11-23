#!/usr/bin/env python3
import requests, time, hashlib

EMULATOR = "http://localhost:5000"
UID = "device001"
OWNER = "alice"
PASSWORD = "alicepw"

def generate_authkey(uid, owner, secret="kalay_secret_2024"):
    """Generate AuthKey (same as emulator)"""
    auth_string = f"{uid}:{owner}:{secret}"
    return hashlib.sha256(auth_string.encode()).hexdigest()[:16]

def register():
    authkey = generate_authkey(UID, OWNER)
    payload = {
        "uid": UID, 
        "owner": OWNER, 
        "password": PASSWORD,
        "authkey": authkey  # Legitimate client includes AuthKey
    }
    r = requests.post(EMULATOR + "/register", json=payload)
    print("register:", r.status_code, r.json())

def get_stream():
    r = requests.get(f"{EMULATOR}/stream/{UID}")
    print("stream:", r.status_code, r.text.strip())

if __name__ == "__main__":
    print("🔐 Legitimate Device Client (with AuthKey support)")
    register()
    time.sleep(0.5)
    get_stream()
