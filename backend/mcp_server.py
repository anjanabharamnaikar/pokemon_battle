# backend/mcp_server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
import json
from pathlib import Path
import random
from battle_simulator import simulate_battle # Assuming you have a battle simulator module
app = FastAPI()

# Enable CORS
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add these CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Load Pokémon data
def load_pokemon_data():
    data_path = Path(__file__).parent / "data/pokemon_data.json"
    try:
        with open(data_path) as f:
            data = json.load(f)
            # Clean the keys: strip whitespace, convert to lowercase, remove special chars
            return {
                k.strip().lower().replace('"', '').replace("'", ""): v 
                for k, v in data.items()
            }
    except Exception as e:
        print(f"ERROR loading data: {str(e)}")
        return {}
pokemon_data = load_pokemon_data()
print("Loaded Pokémon names:", list(pokemon_data.keys()))  # This will show in your server console

# Models
class Pokemon(BaseModel):
    name: str
    types: List[str]
    stats: dict
    moves: List[dict]

# Endpoints
@app.get("/")
async def root():
    return {"status": "Pokémon MCP Server is running"}

@app.get("/pokemon")
async def get_all_pokemon():
    return list(pokemon_data.keys())

@app.get("/pokemon/{name}")
async def get_pokemon(name: str):
    if name.lower() in pokemon_data:
        return pokemon_data[name.lower()]
    return {"error": "Pokémon not found"}

# Add this import at the top
from pydantic import BaseModel
from typing import Optional

# Add this model for battle requests
class BattleRequest(BaseModel):
    pokemon1: str
    pokemon2: str
    rules: Optional[dict] = None  # Optional battle rules

# Replace the GET battle endpoint with this POST endpoint
@app.post("/battle/simulate")
async def simulate_battle(request: BattleRequest):
    try:
        print(f"Received battle request: {request}")  # Debug log
        
        p1 = request.pokemon1.strip().lower()
        p2 = request.pokemon2.strip().lower()
        
        print(f"Looking for: {p1} and {p2}")  # Debug log
        
        if p1 not in pokemon_data:
            return {"error": f"Pokémon {request.pokemon1} not found"}
        if p2 not in pokemon_data:
            return {"error": f"Pokémon {request.pokemon2} not found"}
        
        print("Pokémon found, starting simulation...")  # Debug log
        
        # Get battle data
        pokemon1 = pokemon_data[p1]
        pokemon2 = pokemon_data[p2]
        
        # Simple battle simulation - replace with your actual logic
        winner = p1 if random.random() > 0.5 else p2
        
        print(f"Battle complete. Winner: {winner}")  # Debug log
        
        return {
            "pokemon1": pokemon1["name"],
            "pokemon2": pokemon2["name"],
            "winner": winner,
            "logs": [
                f"{pokemon1['name']} used their move!",
                f"{pokemon2['name']} countered!",
                f"{winner} won the battle!"
            ]
        }
        
    except Exception as e:
        print(f"ERROR in battle simulation: {str(e)}")  # This will show in your server logs
        return {"error": str(e)}
    
@app.get("/test-lookup/{name}")
async def test_lookup(name: str):
    normalized = name.strip().lower().replace('"', '').replace("'", "")
    exists = normalized in pokemon_data
    return {
        "input": name,
        "normalized": normalized,
        "exists": exists,
        "matches": [k for k in pokemon_data.keys() if normalized in k]
    }
# You can keep the GET version too if you want both
@app.get("/battle/{pokemon1}/{pokemon2}")
async def simulate_battle_get(pokemon1: str, pokemon2: str):
    return await simulate_battle(BattleRequest(pokemon1=pokemon1, pokemon2=pokemon2))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)