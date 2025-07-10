import random
import json
import os
from collections import defaultdict, Counter

# Materia categories with weighted choices
materia = {
    "Magic": [
        ("Fire", 10), ("Ice", 10), ("Thunder", 8), ("Wind", 6), ("Bio", 6),
        ("Quake", 5), ("Holy", 3), ("Comet", 4), ("Mystify", 4), ("Seal", 4),
        ("Cure", 10), ("Revive", 5), ("Ultima", 2)
    ],
    "Summon": [
        ("Ifrit", 10), ("Shiva", 10), ("Ramuh", 8), ("Typhoon", 4),
        ("Hades", 4), ("Titan", 6), ("Alexander", 3), ("Bahamut", 4),
        ("Choco/Mog", 10), ("Knights of the round", 1)
    ],
    "Independent": [
        ("HP plus", 10), ("MP plus", 10), ("Long-reach", 5), ("Exp plus", 6),
        ("Luck plus", 4), ("Strength plus", 6), ("Magic plus", 4),
        ("Counterattack", 3), ("Mega-all", 2), ("Underwater", 2)
    ],
    "Support": [
        ("All", 10), ("Added-effect", 8), ("Counter", 5), ("Elemental", 7),
        ("MP Turbo", 4), ("Steal as well", 6), ("Added-cut", 5),
        ("HP Absorb", 4), ("Final Attack", 2)
    ],
    "Command": [
        ("Steal", 8), ("Throw", 6), ("Sense", 6), ("Deathblow", 5),
        ("Mime", 5), ("Double-cut", 4), ("Enemy Skill", 7), ("Manipulate", 6),
        ("Morph", 5), ("W-item", 3), ("W-summon", 2), ("W-magic", 2)
    ]
}

# Map Twitch rewards to Materia categories
reward_to_category = {
    "Redeem Magic Materia": "Magic",
    "Redeem Summon Materia": "Summon",
    "Redeem Independent Materia": "Independent",
    "Redeem Support Materia": "Support",
    "Redeem Command Materia": "Command"
}

SAVE_FILE = "accounts.json"

# 🔄 Load inventory from disk
def load_accounts():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE) as f:
            raw = json.load(f)
        return defaultdict(Counter, {user: Counter(data) for user, data in raw.items()})
    return defaultdict(Counter)

# 💾 Save current state to disk
def save_accounts(accounts):
    with open(SAVE_FILE, "w") as f:
        serializable = {user: dict(counter) for user, counter in accounts.items()}
        json.dump(serializable, f, indent=2)

# Initialize inventory
accounts = load_accounts()

def pick_materia(category):
    items, weights = zip(*materia[category])
    return random.choices(items, weights=weights, k=1)[0]

def handle_redemption(user_name, reward_title):
    if reward_title not in reward_to_category:
        print(f"❌ Unknown reward: {reward_title}")
        return None

    category = reward_to_category[reward_title]
    materia_won = pick_materia(category)
    accounts[user_name][materia_won] += 1
    save_accounts(accounts)

    count = accounts[user_name][materia_won]
    status = "first time!" if count == 1 else f"now owns x{count}"
    print(f"✅ {user_name} redeemed {reward_title} → got: {materia_won} ({status})")

    return materia_won, count

# 🧪 Command-line test loop
if __name__ == "__main__":
    while True:
        user = input("User name: ")
        reward = input("Reward title: ")
        handle_redemption(user, reward)

        print(f"{user}'s inventory: {dict(accounts[user])}")