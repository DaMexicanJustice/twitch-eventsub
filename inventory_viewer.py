from flask import Flask, request, render_template_string
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

# 🎮 Setup Flask
app = Flask(__name__)
load_dotenv()

# 🧠 Setup Database
DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# 🔮 Materia Model
class MateriaInventory(Base):
    __tablename__ = 'inventory'
    user_name = Column(String, primary_key=True)
    materia_name = Column(String, primary_key=True)
    count = Column(Integer, default=1)
    redeemed_at = Column(DateTime(timezone=True))

Base.metadata.create_all(engine)

# 🗂️ Materia type and emoji mappings
materia_categories = {
    "Magic": ["Fire", "Ice", "Thunder", "Wind", "Bio", "Quake", "Holy", "Comet", "Mystify", "Seal", "Cure", "Revive", "Ultima"],
    "Summon": ["Ifrit", "Shiva", "Ramuh", "Typhoon", "Hades", "Titan", "Alexander", "Bahamut", "Choco/Mog", "Knights of the round"],
    "Independent": ["HP plus", "MP plus", "Long-reach", "Exp plus", "Luck plus", "Strength plus", "Magic plus", "Counterattack", "Mega-all", "Underwater"],
    "Support": ["All", "Added-effect", "Counter", "Elemental", "MP Turbo", "Steal as well", "Added-cut", "HP Absorb", "Final Attack"],
    "Command": ["Steal", "Throw", "Sense", "Deathblow", "Mime", "Double-cut", "Enemy Skill", "Manipulate", "Morph", "W-item", "W-summon", "W-magic"]
}

materia_emojis = {
    "Magic": "🟢",
    "Summon": "🔴",
    "Independent": "🟣",
    "Support": "🔵",
    "Command": "🟡"
}

def get_materia_category(name):
    for category, names in materia_categories.items():
        if name in names:
            return category
    return None

# 🧪 Main Page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Materia Inventory Viewer</title>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500&display=swap');

    body {
        background-color: #000000;
        color: #00ffcc;
        font-family: 'Orbitron', sans-serif;
        padding: 2em;
        text-align: center;
    }

    h2 {
        color: #00ffcc;
        text-shadow: 0 0 8px #00ffcc;
    }

    input, button {
        font-family: 'Orbitron', sans-serif;
        background-color: #222;
        color: #00ffcc;
        border: 1px solid #00ffcc;
        padding: 10px;
        margin-top: 1em;
        font-size: 16px;
        border-radius: 5px;
    }

    button:hover {
        background-color: #00ffcc;
        color: #000;
        cursor: pointer;
    }

    table {
        border-collapse: collapse;
        margin-top: 2em;
        width: 85%;
        margin-left: auto;
        margin-right: auto;
        background-color: #111;
    }

    th, td {
        border: 1px solid #00ffcc;
        padding: 8px;
        text-align: center;
        color: #ffffff;
    }

    th {
        background-color: #222;
        text-transform: uppercase;
    }

    td {
        font-size: 14px;
    }
    </style>
</head>
<body>
    <h2>🔮 Materia Inventory Viewer</h2>
    <input type="text" id="userInput" placeholder="Search username..." />
    <button onclick="fetchInventory()">Search</button>

    <div id="resultsArea"></div>

    <script>
    async function fetchInventory() {
        const username = document.getElementById('userInput').value;
        const response = await fetch(`/inventory?user=${encodeURIComponent(username)}`);
        const html = await response.text();
        document.getElementById('resultsArea').innerHTML = html;
    }

    window.onload = fetchInventory;
    </script>
</body>
</html>
"""

# 🌐 Main Page Route
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# 📊 Inventory Data Route
@app.route('/inventory')
def inventory_view():
    session = Session()
    username = request.args.get('user')
    query = session.query(MateriaInventory)

    if username:
        query = query.filter(MateriaInventory.user_name == username)

    results = query.order_by(MateriaInventory.redeemed_at.desc()).all()
    session.close()

    rows = []
    for r in results:
        category = get_materia_category(r.materia_name)
        emoji = materia_emojis.get(category, "⚪")
        styled_name = f"{emoji} {r.materia_name}"
        rows.append(f"""
            <tr>
                <td>{r.user_name}</td>
                <td style="font-weight: bold;">{styled_name}</td>
                <td>{r.count}</td>
                <td>{r.redeemed_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
            </tr>
        """)

    table_html = f"""
    <table>
        <tr>
            <th>User</th><th>Materia</th><th>Count</th><th>Redeemed At</th>
        </tr>
        {''.join(rows)}
    </table>
    """
    return table_html

# 🚀 Launch Viewer
if __name__ == '__main__':
    app.run(debug=True)