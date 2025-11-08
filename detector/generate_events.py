import pandas as pd
import random

uids = [f"user{i}" for i in range(10)]
owners = ["client", "attacker"]
ips = [f"192.168.0.{i}" for i in range(1, 11)]

rows = []
for _ in range(100):
    uid = random.choice(uids)
    owner = random.choice(owners)
    ip = random.choice(ips)
    value = random.random()
    rows.append((uid, owner, ip, value))

df = pd.DataFrame(rows, columns=["uid", "owner", "ip", "value"])
df.to_csv("detector/events.csv", index=False)
print("Generated detector/events.csv with", len(df), "rows")
