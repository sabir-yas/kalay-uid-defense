#!/usr/bin/env python3
import requests, time
EMULATOR = "http://localhost:5000"
UID = "device001"
OWNER = "alice"

def register():
	r = requests.post(EMULATOR+"/register", json={"uid":UID, "owner":OWNER})
	print("register:", r.status_code, r.json())

def get_stream():
	r = requests.get(f"{EMULATOR}/stream/{UID}")
	print("stream:", r.status_code, r.text.strip())	
if __name__=="__main__":
	register()
	time.sleep(0.5)
	get_stream()
