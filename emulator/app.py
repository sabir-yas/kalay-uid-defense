#!/usr/bin/env python3
from flask import Flask, request, jsonify
import json, os, time, logging

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DB_FILE = os.path.join(SCRIPT_DIR, 'uids.json')

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
if not os.path.exists(DB_FILE):
	os.makedirs(SCRIPT_DIR, exist_ok=True)
	with open(DB_FILE,'w') as f: json.dump({}, f)

app = Flask(__name__)

def read_db():
	with open(DB_FILE,'r') as f: return json.load(f)
def write_db(d):
	with open(DB_FILE,'w') as f: json.dump(d, f, indent=2)

@app.route("/register", methods=["POST"])
def register():
	data = request.json or {}
	uid = data.get("uid")
	owner = data.get("owner", "unknown")
	db = read_db()
	previous = db.get(uid)
	db[uid] = {"owner":owner, "last_seen": time.time(), "ip": request.remote_addr}
	write_db(db)
	logging.info("REGISTER uid=%s owner=%s from=%s prev=%s", uid, owner, request.remote_addr, previous)
	return jsonify({"status":"ok","previous":previous}), 200

@app.route("/stream/<uid>", methods=["GET"])
def stream(uid):
	db = read_db()
	if uid not in db:
		return "UID not registered\n", 404
	return f"MOCKSTREAM for {uid} owner={db[uid]['owner']}\n", 200

@app.route("/uids", methods=["GET"])
def uids():
	return jsonify(read_db())

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000)
