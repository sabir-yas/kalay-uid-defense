# Kalay UID Impersonation Defense System

A comprehensive security framework demonstrating layered defense against UID impersonation attacks in IoT/Kalay device networks. This system combines **AuthKey cryptographic authentication** with **Moving Target Defense (MTD)** to protect against device takeover attempts.

## Features

- **AuthKey Authentication** - Cryptographic device verification
- **Moving Target Defense** - Dynamic UID decoys to trap attackers
- **Real-time Security Monitoring** - Live attack detection and alerting
- **Attack Simulation** - Realistic UID impersonation attack testing
- **Layered Security** - Combined defenses for maximum protection

## Prerequisites

- Python 3.8+
- Flask
- Requests library

## Quick Start

### 1. Clone & Install
```
git clone https://github.com/sabir-yas/kalay-uid-defense.git
cd kalay-uid-defense
pip install flask requests
```

### 2. Start the Security System
**Terminal 1 - Emulator:**
```
python3 app.py
```

**Terminal 2 - Security Monitor:**
```
python3 security_monitor.py
```

**Terminal 3 - Enable Protection:**
```
python3 security_controller.py full
```

### 3. Test the System
**Terminal 4 - Legitimate Client:**
```
python3 client.py
```

**Terminal 5 - Simulate Attack:**
```
python3 attacker.py
```

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Legitimate    │    │  Security        │    │   Attacker      │
│   Client        │───▶│  Emulator        │◀──▶│  Simulation     │
│                 │    │  (AuthKey+MTD)   │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │  Security        │
                     │  Monitor         │
                     └──────────────────┘
```

## Project Structure

```
kalay-uid-defense/
├── app.py                    # Main emulator with AuthKey + MTD
├── security_monitor.py       # Real-time security monitoring
├── security_controller.py    # Security management CLI
├── client.py                 # Legitimate device client
├── attacker.py               # UID impersonation attacker
├── utilities/
│   ├── uids.json             # Device database
│   └── spoofed_uids.json     # MTD decoy database
└── README.md
```

## How It Works

### AuthKey Protection
- Cryptographic authentication using SHA-256 hashes
- Prevents unauthorized device registration
- Ensures only legitimate owners can access devices

### Moving Target Defense
- Deploys decoy UIDs that appear legitimate
- Traps attackers attempting device takeover
- Provides early warning of attack attempts

### Security Monitoring
- Real-time detection of suspicious activities
- Owner change detection and alerting
- Comprehensive security status reporting

## Usage Examples

### Enable Full Protection
```
python3 security_controller.py full
```

### Check Security Status
```
python3 security_controller.py status
```

### Enable Specific Defenses
```
# AuthKey only
python3 security_controller.py authkey_only

# MTD only  
python3 security_controller.py mtd_only

# Disable all defenses (vulnerable mode)
python3 security_controller.py vulnerable
```

### Manage MTD Traps
```
# Generate decoys
python3 security_controller.py generate_traps 20

# View trap status
python3 security_controller.py traps

# Reset system
python3 security_controller.py reset
```

## Expected Output

### Security Status
```
📊 SECURITY STATUS OVERVIEW
========================================
AuthKey Protection:    🔐 ENABLED
MTD Protection:        🎯 ENABLED
Active Clients:        3
UID Changes Detected:  0
MTD Traps TriggerED:   2

🏆 SECURITY LEVEL: MAXIMUM PROTECTION
```

### Attack Results
```
📊 ATTACK SUMMARY REPORT
==================================================
Targets Attempted: 5
✅ Compromised: 0
🔐 Blocked by AuthKey: 3
🎯 Trapped by MTD: 2

🛡️ SUCCESS: All attacks prevented by security defenses!
```

## API Endpoints

### Emulator (`app.py`)
- `POST /register` - Device registration
- `GET /stream/<uid>` - Device access
- `POST /config` - Security configuration
- `GET /stats` - System statistics
- `POST /mtd/generate_spoofed` - Generate MTD decoys

### Security Monitor
- Continuous monitoring of registration patterns
- Real-time alerting for suspicious activities

## Security Controller Commands

| Command             | Description                       |
|--------------------|-----------------------------------|
| `full`             | Enable AuthKey + MTD protection   |
| `authkey_only`     | Enable only AuthKey protection    |
| `mtd_only`         | Enable only MTD protection        |
| `vulnerable`       | Disable all defenses              |
| `status`           | Show security status              |
| `generate_traps N` | Generate N MTD decoys             |
| `traps`            | Show MTD trap status              |
| `reset`            | Reset entire system               |

## Research Value

This project demonstrates:
- **Layered security** for IoT devices
- **Moving Target Defense** practical implementation
- **UID impersonation** attack mitigation
- **Real-time security monitoring** techniques

## Troubleshooting

### Common Issues

**Emulator not starting:**
```
# Check if port 5000 is available
netstat -tulpn | grep 5000
```

**Cannot connect to security monitor:**
- Ensure `security_monitor.py` is running before controller
- Check firewall settings

**Attack simulation not working:**
- Verify defenses are enabled: `python3 security_controller.py status`
- Check emulator is running on port 5000

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on research into Kalay protocol security
- Moving Target Defense concepts from cybersecurity research
- IoT security best practices

---
