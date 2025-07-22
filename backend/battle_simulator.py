from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import json
from pathlib import Path
import random  # Make sure this import is at the top

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Pokémon data
def load_pokemon_data():
    data_path = Path(__file__).parent / "data/pokemon_data.json"
    try:
        with open(data_path) as f:
            data = json.load(f)
            return {
                k.strip().lower(): v 
                for k, v in data.items()
            }
    except Exception as e:
        print(f"ERROR loading data: {str(e)}")
        return {}

pokemon_data = load_pokemon_data()
print("Loaded Pokémon:", list(pokemon_data.keys()))

# Models
class BattleRequest(BaseModel):
    pokemon1: str
    pokemon2: str
    rules: Optional[dict] = None

# Endpoints
@app.get("/")
async def root():
    return {"status": "Pokémon MCP Server is running"}

@app.get("/pokemon")
async def get_all_pokemon():
    return list(pokemon_data.keys())

@app.get("/pokemon/{name}")
async def get_pokemon(name: str):
    normalized = name.strip().lower()
    if normalized in pokemon_data:
        return pokemon_data[normalized]
    return {"error": f"Pokémon {name} not found"}

@app.post("/battle/simulate")
async def simulate_battle(request: BattleRequest):
    try:
        p1 = request.pokemon1.strip().lower()
        p2 = request.pokemon2.strip().lower()
        
        if p1 not in pokemon_data:
            return {"error": f"Pokémon {request.pokemon1} not found. Available: {list(pokemon_data.keys())}"}
        if p2 not in pokemon_data:
            return {"error": f"Pokémon {request.pokemon2} not found. Available: {list(pokemon_data.keys())}"}
        
        # Simple battle logic - replace with your actual implementation
        winner = p1 if random.random() > 0.5 else p2
        
        return {
            "pokemon1": pokemon_data[p1]["name"],
            "pokemon2": pokemon_data[p2]["name"],
            "winner": winner,
            "logs": [
                f"Round 1: {pokemon_data[p1]['name']} attacks!",
                f"Round 1: {pokemon_data[p2]['name']} defends!",
                f"Final: {winner} wins!"
            ]
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)