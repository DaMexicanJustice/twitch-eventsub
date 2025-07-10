import json

# Save
with open("accounts.json", "w") as f:
    json.dump(accounts, f)

# Load
with open("accounts.json") as f:
    raw = json.load(f)
    accounts = defaultdict(Counter, {k: Counter(v) for k, v in raw.items()})