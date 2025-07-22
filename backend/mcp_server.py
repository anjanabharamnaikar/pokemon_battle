import os
import sys
import json
import random
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
from transformers import pipeline

# ----------------------------------------
# Environment and Path Setup
# ----------------------------------------

load_dotenv()

venv_path = "/Users/anjanabharamnaikar/Downloads/pokemon-battle-mcp-server/venv"
for p in [
    f"{venv_path}/lib/python3.13/site-packages",  # macOS/Linux
    f"{venv_path}/Lib/site-packages"              # Windows
]:
    if os.path.exists(p):
        sys.path.append(p)
        break

# ----------------------------------------
# MCP Core Classes
# ----------------------------------------

class McpServer:
    def __init__(self, name: str, version: str, description: str):
        self.name = name
        self.version = version
        self.description = description
        self.resources = {}
        self.tools = {}

    def register_resource(self, resource):
        self.resources[resource.name] = resource

    def register_tool(self, tool):
        self.tools[tool.name] = tool

class McpResource:
    def __init__(self):
        self.name = ""
        self.description = ""

    async def execute(self, params: Dict) -> Dict:
        return {}

class McpTool:
    def __init__(self):
        self.name = ""
        self.description = ""

    async def execute(self, params: Dict) -> Dict:
        return {}

# ----------------------------------------
# LLM Handler
# ----------------------------------------


class McpModel:
    def __init__(self, server, system_prompt: str):
        self.server = server
        self.system_prompt = system_prompt
        self.model = pipeline("text-generation", model="EleutherAI/gpt-neo-1.3B")

    async def process(self, prompt: str, context: Optional[Dict] = None) -> Dict:
        try:
            enhanced_prompt = f"{self.system_prompt}\n\nUser: {prompt}\nAssistant:"
            response = self.model(
                enhanced_prompt,
                max_new_tokens=100,
                pad_token_id=50256,       # EOS token for GPT-Neo
                truncation=True,
                return_full_text=False    # Only return the new part
            )[0]['generated_text']
            return {"response": response.strip()}
        except Exception as e:
            return {"response": f"LLM error: {str(e)}"}


# ----------------------------------------
# Server Setup
# ----------------------------------------

mcp_server = McpServer(
    name="Pokemon Battle Server",
    version="1.0",
    description="Provides Pokémon data and battle simulation"
)

model_instance = McpModel(mcp_server, "You are a Pokémon battle expert.")

# ----------------------------------------
# Load Pokémon Data
# ----------------------------------------

def load_pokemon_data():
    data_path = Path(__file__).parent / "data/pokemon_data.json"
    try:
        with open(data_path) as f:
            data = json.load(f)
            return {k.lower(): v for k, v in data.items()}
    except Exception as e:
        print(f"Error loading Pokémon data: {e}")
        return {}

pokemon_data = load_pokemon_data()

# ----------------------------------------
# Tools and Resources
# ----------------------------------------

class PokemonResource(McpResource):
    def __init__(self):
        super().__init__()
        self.name = "pokemon_data"
        self.description = "Access Pokémon information"
        self.data = pokemon_data

    async def execute(self, params: Dict) -> Dict:
        name = params.get("name", "").lower()
        return self.data.get(name, {"error": f"Pokémon {name} not found"})

class BattleTool(McpTool):
    def __init__(self):
        super().__init__()
        self.name = "pokemon_battle"
        self.description = "Simulate Pokémon battles"

    async def execute(self, params: Dict) -> Dict:
        p1 = params.get("pokemon1", "").lower()
        p2 = params.get("pokemon2", "").lower()

        if p1 not in pokemon_data or p2 not in pokemon_data:
            return {"error": "One or both Pokémon not found"}

        winner = p1 if random.random() > 0.5 else p2
        return {
            "pokemon1": p1,
            "pokemon2": p2,
            "winner": winner,
            "logs": [
                f"{p1} used a move!",
                f"{p2} countered!",
                f"{winner} won the battle!"
            ]
        }

mcp_server.register_resource(PokemonResource())
mcp_server.register_tool(BattleTool())

# ----------------------------------------
# FastAPI App Setup
# ----------------------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------
# Models
# ----------------------------------------

class BattleRequest(BaseModel):
    pokemon1: str
    pokemon2: str

class LLMRequest(BaseModel):
    prompt: str

# ----------------------------------------
# Utility
# ----------------------------------------

def calculate_damage(attacker, defender) -> int:
    attack = attacker["stats"]["attack"]
    defense = defender["stats"]["defense"]
    base_damage = max(5, int((attack - defense) * 0.5))
    return max(1, base_damage + random.randint(-2, 2))

# ----------------------------------------
# Endpoints
# ----------------------------------------

@app.get("/")
async def root():
    return {"status": "Pokémon Battle Server is running"}

@app.get("/pokemon")
async def get_pokemon_list():
    return {"pokemon": list(pokemon_data.keys())}

@app.get("/pokemon/{name}")
async def get_pokemon(name: str):
    name = name.lower()
    if name not in pokemon_data:
        raise HTTPException(status_code=404, detail="Pokémon not found")
    return pokemon_data[name]

@app.post("/battle/simulate")
async def simulate_battle(request: BattleRequest):
    p1_name = request.pokemon1.lower()
    p2_name = request.pokemon2.lower()

    p1 = pokemon_data.get(p1_name)
    p2 = pokemon_data.get(p2_name)

    if not p1 or not p2:
        return {"error": "Invalid Pokémon names"}

    def type_effectiveness(move_type, defender_types):
        chart = {
            "Electric": {"Water": 2, "Flying": 2, "Electric": 0.5, "Ground": 0},
            "Fire": {"Grass": 2, "Ice": 2, "Bug": 2, "Steel": 2, "Fire": 0.5, "Water": 0.5, "Rock": 0.5},
            "Water": {"Fire": 2, "Rock": 2, "Ground": 2, "Water": 0.5, "Grass": 0.5},
            "Grass": {"Water": 2, "Ground": 2, "Rock": 2, "Fire": 0.5, "Flying": 0.5},
            "Flying": {"Grass": 2, "Fighting": 2, "Bug": 2, "Electric": 0.5},
            "Steel": {"Ice": 2, "Rock": 2, "Fairy": 2, "Water": 0.5, "Fire": 0.5},
            "Ice": {"Flying": 2, "Grass": 2, "Ground": 2, "Dragon": 2},
            "Dragon": {"Dragon": 2},
            "Normal": {"Rock": 0.5, "Ghost": 0}
        }
        multiplier = 1.0
        for dtype in defender_types:
            multiplier *= chart.get(move_type, {}).get(dtype, 1.0)
        return multiplier

    def calculate_damage(attacker, defender, move):
        atk_stat = attacker["stats"]["attack"]
        def_stat = defender["stats"]["defense"]
        power = move.get("power", 0)

        if power == 0:
            return 0

        # STAB
        stab = 1.5 if move["type"] in attacker["types"] else 1.0
        effectiveness = type_effectiveness(move["type"], defender["types"])
        random_factor = random.uniform(0.85, 1.0)

        damage = (((2 * 50 / 5 + 2) * power * (atk_stat / def_stat)) / 50 + 2) * stab * effectiveness * random_factor
        return max(1, int(damage))

    def choose_move(pokemon):
        return random.choice(pokemon["moves"])

    p1_hp = p1["stats"]["hp"]
    p2_hp = p2["stats"]["hp"]
    battle_log = []

    turn = 1
    while p1_hp > 0 and p2_hp > 0:
        battle_log.append(f"--- Turn {turn} ---")

        if p1["stats"]["speed"] >= p2["stats"]["speed"]:
            first, second = (p1, p2)
            first_hp, second_hp = (p1_hp, p2_hp)
        else:
            first, second = (p2, p1)
            first_hp, second_hp = (p2_hp, p1_hp)

        first_move = choose_move(first)
        damage = calculate_damage(first, second, first_move)
        second_hp -= damage
        battle_log.append(f"{first['name']} used {first_move['name']}! It dealt {damage} damage.")

        if second_hp <= 0:
            winner = first["name"]
            break

        second_move = choose_move(second)
        damage = calculate_damage(second, first, second_move)
        first_hp -= damage
        battle_log.append(f"{second['name']} responded with {second_move['name']}! It dealt {damage} damage.")

        if first == p1:
            p1_hp, p2_hp = first_hp, second_hp
        else:
            p2_hp, p1_hp = first_hp, second_hp

        if first_hp <= 0:
            winner = second["name"]
            break

        turn += 1

    if p1_hp > 0 and p2_hp <= 0:
        winner = p1["name"]
    elif p2_hp > 0 and p1_hp <= 0:
        winner = p2["name"]
    else:
        winner = "Draw"

    return {
        "winner": winner,
        "logs": battle_log,
        "hp_remaining": {
            p1["name"]: max(0, p1_hp),
            p2["name"]: max(0, p2_hp)
        }
    }


@app.post("/llm/interact")
async def llm_interact(request: LLMRequest):
    return await model_instance.process(request.prompt)

# ----------------------------------------
# Run Server
# ----------------------------------------

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)