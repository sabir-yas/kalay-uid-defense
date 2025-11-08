#!/usr/bin/env python3
from flask import Flask, request, jsonify
import json, os, time, logging
DB_FILE = 'uids.json'
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
if not os.path.exists(DB_FILE):
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
    password = data.get("password")
    db = read_db()
    if uid in db and db[uid].get("owner") != owner:
        # require password to change owner (demo)
        if password != "letmein":
            logging.info("REJECT overwrite uid=%s tried_by=%s ip=%s", uid, owner, request.remote_addr)
            return jsonify({"status":"denied","reason":"cannot overwrite owner without credentials"}), 403
    previous = db.get(uid)
    db[uid] = {"owner": owner, "last_seen": time.time(), "ip": request.remote_addr}
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
