#!/usr/bin/env python3
from flask import Flask, request, jsonify
import json, os, time, logging, hashlib, random, string

DB_FILE = 'uids.json'
FAIL_DB_FILE = 'failures.json'
SPOOFED_UIDS_FILE = 'spoofed_uids.json'
AUTHKEY_ENABLED = False
DTLS_ENABLED = False
MTD_ENABLED = False  # Moving Target Defense

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

# Initialize files
for file in [DB_FILE, SPOOFED_UIDS_FILE]:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump({}, f)

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def generate_authkey(uid, owner, secret="kalay_secret_2024"):
    auth_string = f"{uid}:{owner}:{secret}"
    return hashlib.sha256(auth_string.encode()).hexdigest()[:16]

def generate_spoofed_uid():
    """Generate random spoofed UIDs that look legitimate"""
    prefixes = ['cam', 'device', 'baby', 'security', 'iot', 'sensor']
    prefix = random.choice(prefixes)
    suffix = ''.join(random.choices(string.digits, k=6))
    return f"{prefix}{suffix}"

app = Flask(__name__)

def read_db():
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def write_db(d):
    with open(DB_FILE, 'w') as f:
        json.dump(d, f, indent=2)

def read_spoofed_uids():
    with open(SPOOFED_UIDS_FILE, 'r') as f:
        return json.load(f)

def write_spoofed_uids(d):
    with open(SPOOFED_UIDS_FILE, 'w') as f:
        json.dump(d, f, indent=2)

# 🔄 Reset endpoint
@app.route("/reset", methods=["POST"])
def reset_database():
    try:
        with open(DB_FILE, 'w') as f:
            json.dump({}, f)
        with open(SPOOFED_UIDS_FILE, 'w') as f:
            json.dump({}, f)
        if os.path.exists(FAIL_DB_FILE):
            os.remove(FAIL_DB_FILE)
        
        logging.info("DATABASE RESET: All UIDs and spoofed records cleared")
        return jsonify({"status": "success", "message": "System reset complete"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    uid = data.get("uid")
    owner = data.get("owner", "unknown")
    password = data.get("password")
    authkey = data.get("authkey")
    ip = request.remote_addr
    now = time.time()
    
    db = read_db()
    spoofed_db = read_spoofed_uids()
    
    # 🎯 MOVING TARGET DEFENSE: Check if this is a known spoofed UID
    if MTD_ENABLED and uid in spoofed_db:
        logging.warning("🚨 MTD TRAP: Attacker used spoofed UID %s from %s - BLOCKING", uid, ip)
        # Track the attacker
        spoofed_db[uid]['attack_attempts'] = spoofed_db[uid].get('attack_attempts', 0) + 1
        spoofed_db[uid]['last_attempt'] = now
        spoofed_db[uid]['attacker_ips'] = list(set(spoofed_db[uid].get('attacker_ips', []) + [ip]))
        write_spoofed_uids(spoofed_db)
        
        return jsonify({
            "status": "denied", 
            "reason": "registration failed",
            "actual_reason": "MTD_TRAP"  # Don't reveal it's a spoofed UID
        }), 403
    
    # 🔒 AuthKey Validation
    if AUTHKEY_ENABLED:
        if not authkey:
            return jsonify({"status": "denied", "reason": "AuthKey required"}), 403
        expected_authkey = generate_authkey(uid, owner)
        if authkey != expected_authkey:
            return jsonify({"status": "denied", "reason": "Invalid AuthKey"}), 403
    
    # Existing registration logic...
    if db.get(uid) and db[uid].get("owner") != owner:
        if not password or hash_password(password) != db[uid].get("password_hash", ""):
            logging.warning("SUSPICIOUS: UID takeover attempt %s by %s from %s", uid, owner, ip)
            return jsonify({"status": "denied", "reason": "authentication failed"}), 403
    
    # Register/update
    db[uid] = {
        "owner": owner,
        "password_hash": hash_password(password) if password else "",
        "authkey": authkey,
        "last_seen": now,
        "ip": ip,
        "registered_at": db[uid].get('registered_at', now) if uid in db else now,
        "secure_registration": AUTHKEY_ENABLED,
        "mtd_protected": MTD_ENABLED
    }
    
    write_db(db)
    
    security_level = "🔐 SECURE" if AUTHKEY_ENABLED else "⚠️ INSECURE"
    mtd_status = " + 🎯 MTD" if MTD_ENABLED else ""
    logging.info("REGISTERED: %s%s - uid=%s owner=%s", security_level, mtd_status, uid, owner)
    
    return jsonify({"status": "ok", "secure": AUTHKEY_ENABLED, "mtd": MTD_ENABLED})

@app.route("/stream/<uid>", methods=["GET"])
def stream(uid):
    db = read_db()
    if uid not in db:
        return "UID not registered\n", 404
    
    owner = db[uid]["owner"]
    secure = db[uid].get("secure_registration", False)
    mtd = db[uid].get("mtd_protected", False)
    
    security_icons = "🔐" if secure else "⚠️"
    mtd_icon = "🎯" if mtd else ""
    
    return f"STREAM_DATA: {security_icons}{mtd_icon} Camera feed for {uid} owned by {owner}\n", 200

# 🎯 NEW: MTD Management Endpoints
@app.route("/mtd/generate_spoofed", methods=["POST"])
def generate_spoofed_uids():
    """Generate spoofed UIDs for moving target defense"""
    data = request.json or {}
    count = data.get('count', 10)
    
    spoofed_db = read_spoofed_uids()
    generated = []
    
    for i in range(count):
        spoofed_uid = generate_spoofed_uid()
        spoofed_db[spoofed_uid] = {
            "created_at": time.time(),
            "purpose": "mtd_trap",
            "attack_attempts": 0,
            "attacker_ips": []
        }
        generated.append(spoofed_uid)
    
    write_spoofed_uids(spoofed_db)
    logging.info("🎯 MTD: Generated %d spoofed UIDs", count)
    
    return jsonify({
        "status": "success",
        "generated": generated,
        "total_spoofed": len(spoofed_db)
    })

@app.route("/mtd/traps", methods=["GET"])
def get_mtd_traps():
    """Get info about MTD traps and caught attackers"""
    spoofed_db = read_spoofed_uids()
    traps_triggered = sum(1 for uid in spoofed_db.values() if uid.get('attack_attempts', 0) > 0)
    
    return jsonify({
        "total_traps": len(spoofed_db),
        "traps_triggered": traps_triggered,
        "total_attempts": sum(uid.get('attack_attempts', 0) for uid in spoofed_db.values()),
        "spoofed_uids": list(spoofed_db.keys())[:10]  # First 10 for preview
    })

@app.route("/config", methods=["POST"])
def set_config():
    global AUTHKEY_ENABLED, DTLS_ENABLED, MTD_ENABLED
    data = request.json or {}
    AUTHKEY_ENABLED = data.get('authkey', AUTHKEY_ENABLED)
    DTLS_ENABLED = data.get('dtls', DTLS_ENABLED)
    MTD_ENABLED = data.get('mtd', MTD_ENABLED)
    
    status_msgs = []
    if AUTHKEY_ENABLED: status_msgs.append("AuthKey🔐")
    if MTD_ENABLED: status_msgs.append("MTD🎯")
    if DTLS_ENABLED: status_msgs.append("DTLS🔒")
    
    status = " + ".join(status_msgs) if status_msgs else "VULNERABLE⚠️"
    logging.info("🔧 SECURITY CONFIG: %s", status)
    
    return jsonify({
        "authkey_enabled": AUTHKEY_ENABLED,
        "dtls_enabled": DTLS_ENABLED, 
        "mtd_enabled": MTD_ENABLED,
        "message": f"Security: {status}"
    })

@app.route("/uids", methods=["GET"])
def get_uids():
    db = read_db()
    return jsonify(db)

@app.route("/stats", methods=["GET"])
def stats():
    db = read_db()
    spoofed_db = read_spoofed_uids()
    secure_count = sum(1 for device in db.values() if device.get("secure_registration"))
    mtd_count = sum(1 for device in db.values() if device.get("mtd_protected"))
    
    return jsonify({
        "total_devices": len(db),
        "secure_devices": secure_count,
        "mtd_protected_devices": mtd_count,
        "spoofed_uids_count": len(spoofed_db),
        "authkey_enabled": AUTHKEY_ENABLED,
        "mtd_enabled": MTD_ENABLED,
        "security_status": "protected" if (AUTHKEY_ENABLED or MTD_ENABLED) else "vulnerable"
    })

if __name__ == "__main__":
    print("🔄 Kalay Emulator with MTD Started!")
    print("   MTD endpoints: /mtd/generate_spoofed, /mtd/traps")
    app.run(host="0.0.0.0", port=5000, debug=True)
