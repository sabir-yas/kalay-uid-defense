#!/usr/bin/env python3
from flask import Flask, request, jsonify
import json, os, time, logging, hashlib

DB_FILE = 'uids.json'
FAIL_DB_FILE = 'failures.json'
AUTHKEY_ENABLED = False  # Simulate vulnerable vs secure configurations
DTLS_ENABLED = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

# Initialize database file if it doesn't exist
if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w') as f:
        json.dump({}, f)

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def generate_authkey(uid, owner, secret="kalay_secret_2024"):
    """Generate a proper AuthKey (simplified for demo)"""
    import hashlib
    auth_string = f"{uid}:{owner}:{secret}"
    return hashlib.sha256(auth_string.encode()).hexdigest()[:16]

app = Flask(__name__)

def read_db():
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def write_db(d):
    with open(DB_FILE, 'w') as f:
        json.dump(d, f, indent=2)

# 🔄 Reset endpoint
@app.route("/reset", methods=["POST"])
def reset_database():
    """Reset all registrations - for testing and demo purposes"""
    try:
        with open(DB_FILE, 'w') as f:
            json.dump({}, f)
        if os.path.exists(FAIL_DB_FILE):
            os.remove(FAIL_DB_FILE)
        
        logging.info("DATABASE RESET: All UIDs and failure records cleared")
        return jsonify({
            "status": "success", 
            "message": "All device registrations and security records have been reset"
        }), 200
    except Exception as e:
        logging.error("Reset failed: %s", e)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    uid = data.get("uid")
    owner = data.get("owner", "unknown")
    password = data.get("password")
    authkey = data.get("authkey")  # Kalay AuthKey feature
    ip = request.remote_addr
    now = time.time()
    
    db = read_db()
    entry = db.get(uid)
    
    # 🔒 DEFENSE: AuthKey Validation
    if AUTHKEY_ENABLED:
        if not authkey:
            logging.warning("🚨 BLOCKED: AuthKey required but not provided for UID %s from %s", uid, ip)
            return jsonify({
                "status": "denied", 
                "reason": "AuthKey required for registration",
                "security_level": "high"
            }), 403
        
        # Validate AuthKey format and value
        expected_authkey = generate_authkey(uid, owner)
        if authkey != expected_authkey:
            logging.warning("🚨 BLOCKED: Invalid AuthKey for UID %s from %s", uid, ip)
            return jsonify({
                "status": "denied", 
                "reason": "Invalid AuthKey - authentication failed",
                "security_level": "high"
            }), 403
        else:
            logging.info("🔐 AuthKey validation successful for UID %s", uid)
    # 🔒 END DEFENSE
    
    # If UID exists, check if this is a legitimate owner change
    if entry and entry.get("owner") != owner:
        if not password or hash_password(password) != entry.get("password_hash", ""):
            logging.warning("SUSPICIOUS: UID takeover attempt %s by %s from %s", uid, owner, ip)
            return jsonify({"status": "denied", "reason": "authentication failed"}), 403
    
    # Register/update the device
    db[uid] = {
        "owner": owner,
        "password_hash": hash_password(password) if password else "",
        "authkey": authkey,
        "last_seen": now,
        "ip": ip,
        "registered_at": entry.get('registered_at', now) if entry else now,
        "version": data.get('sdk_version', 'unknown'),
        "secure_registration": AUTHKEY_ENABLED  # Track if this was a secure registration
    }
    
    write_db(db)
    
    if AUTHKEY_ENABLED:
        logging.info("🔐 SECURE REGISTRATION: uid=%s owner=%s ip=%s", uid, owner, ip)
    else:
        logging.info("⚠️  INSECURE REGISTRATION: uid=%s owner=%s ip=%s", uid, owner, ip)
        
    return jsonify({"status": "ok", "secure": AUTHKEY_ENABLED})

@app.route("/stream/<uid>", methods=["GET"])
def stream(uid):
    db = read_db()
    if uid not in db:
        return "UID not registered\n", 404
    
    owner = db[uid]["owner"]
    secure = db[uid].get("secure_registration", False)
    security_indicator = "🔐" if secure else "⚠️"
    
    # Simulate video/audio stream redirection
    return f"STREAM_DATA: {security_indicator} Camera feed for {uid} owned by {owner} (Secure: {secure})\n", 200

@app.route("/uids", methods=["GET"])
def get_uids():
    """Endpoint to get all registered UIDs - for monitoring"""
    db = read_db()
    return jsonify(db)

# Add endpoints to simulate different security configurations
@app.route("/config", methods=["POST"])
def set_config():
    global AUTHKEY_ENABLED, DTLS_ENABLED
    data = request.json or {}
    AUTHKEY_ENABLED = data.get('authkey', AUTHKEY_ENABLED)
    DTLS_ENABLED = data.get('dtls', DTLS_ENABLED)
    
    status = "enabled" if AUTHKEY_ENABLED else "disabled"
    logging.info("🔧 SECURITY CONFIG: AuthKey %s, DTLS %s", 
                 status, "enabled" if DTLS_ENABLED else "disabled")
    
    return jsonify({
        "authkey_enabled": AUTHKEY_ENABLED, 
        "dtls_enabled": DTLS_ENABLED,
        "message": f"AuthKey protection {status}"
    })

@app.route("/stats", methods=["GET"])
def stats():
    db = read_db()
    secure_count = sum(1 for device in db.values() if device.get("secure_registration"))
    
    return jsonify({
        "total_devices": len(db),
        "secure_devices": secure_count,
        "insecure_devices": len(db) - secure_count,
        "authkey_enabled": AUTHKEY_ENABLED,
        "dtls_enabled": DTLS_ENABLED,
        "security_status": "protected" if AUTHKEY_ENABLED else "vulnerable"
    })

if __name__ == "__main__":
    print("🔄 Kalay Emulator Started!")
    print("   Reset endpoint: POST http://localhost:5000/reset")
    print("   Config endpoint: POST http://localhost:5000/config")
    print("   Stats endpoint: GET http://localhost:5000/stats")
    print(f"   Current security: AuthKey={'🔐 ENABLED' if AUTHKEY_ENABLED else '⚠️ DISABLED'}")
    app.run(host="0.0.0.0", port=5000, debug=True)
