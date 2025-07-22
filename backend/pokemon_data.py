import json
from pathlib import Path
from typing import Dict, Any, List
from pydantic import BaseModel

class PokemonStats(BaseModel):
    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int

class PokemonMove(BaseModel):
    name: str
    power: int
    accuracy: int
    type: str
    effect: str

class Pokemon(BaseModel):
    id: int
    name: str
    types: List[str]
    abilities: List[str]
    stats: PokemonStats
    moves: List[PokemonMove]
    evolution_chain: List[str]

class PokemonDataResource:
    def __init__(self, data_file: str = "data/pokemon_data.json"):
        self.data = self._load_data(data_file)
    
    def _load_data(self, data_file: str) -> Dict[str, Any]:
        path = Path(__file__).parent / data_file
        with open(path, 'r') as f:
            return json.load(f)
    
    def get_pokemon(self, name: str) -> Pokemon:
        pokemon_data = self.data.get(name.lower())
        if not pokemon_data:
            raise ValueError(f"Pokémon {name} not found")
        
        return Pokemon(
            id=pokemon_data['id'],
            name=pokemon_data['name'],
            types=pokemon_data['types'],
            abilities=pokemon_data['abilities'],
            stats=PokemonStats(**pokemon_data['stats']),
            moves=[PokemonMove(**move) for move in pokemon_data['moves']],
            evolution_chain=pokemon_data['evolution_chain']
        )
    
    def get_all_pokemon_names(self) -> List[str]:
        return list(self.data.keys())
    
    def get_pokemon_details(self, name: str) -> Dict[str, Any]:
        pokemon = self.get_pokemon(name)
        return pokemon.dict()