import streamlit as st
import requests
import time
import random

# Configuration
BACKEND_URL = "http://localhost:8001"

# Page setup
st.set_page_config(page_title="Pokémon Battle Arena", page_icon="⚡")
st.title("Pokémon Battle Arena")
st.write("Choose two Pokémon and watch them battle using our Model Context Protocol server!")

# Fetch Pokémon list with error handling
@st.cache_data
def get_pokemon_list():
    try:
        response = requests.get(f"{BACKEND_URL}/pokemon", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch Pokémon list: {str(e)}")
        return ["pikachu", "charmander", "squirtle"]  # Fallback list

pokemon_list = get_pokemon_list()

# Safe default selection
def get_default_index(options, preferred_names):
    for name in preferred_names:
        try:
            return options.index(name.lower())
        except ValueError:
            continue
    return 0  # Fallback to first option

# Battle setup
st.header("Battle Setup")
col1, col2 = st.columns(2)

with col1:
    default_p1 = get_default_index(pokemon_list, ["chartzard", "charmander", "pikachu"])
    pokemon1 = st.selectbox("First Pokémon", pokemon_list, index=default_p1)

with col2:
    default_p2 = get_default_index(pokemon_list, ["pikachu", "squirtle", "charmander"])
    pokemon2 = st.selectbox("Second Pokémon", pokemon_list, index=default_p2)

# Get Pokémon details with better error handling
@st.cache_data
def get_pokemon_details(name):
    try:
        response = requests.post(
            f"{BACKEND_URL}/pokemon/{name}",
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch details for {name}: {str(e)}")
        return None

# Display Pokémon info
pokemon1_details = get_pokemon_details(pokemon1)
pokemon2_details = get_pokemon_details(pokemon2)

if pokemon1_details and pokemon2_details:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(pokemon1_details.get('name', pokemon1).title())
        st.write(" / ".join(pokemon1_details.get('types', ['Unknown'])))
        stats = pokemon1_details.get('stats', {})
        st.write(f"Base Stat Total: {sum(stats.values()) if stats else 'Unknown'}")
    
    with col2:
        st.subheader(pokemon2_details.get('name', pokemon2).title())
        st.write(" / ".join(pokemon2_details.get('types', ['Unknown'])))
        stats = pokemon2_details.get('stats', {})
        st.write(f"Base Stat Total: {sum(stats.values()) if stats else 'Unknown'}")

# Battle simulation function
def run_battle(pokemon1, pokemon2):
    try:
        response = requests.post(
            f"{BACKEND_URL}/battle/simulate",
            json={"pokemon1": pokemon1, "pokemon2": pokemon2},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Battle failed: {str(e)}")
        return None

# Battle button
if st.button("Start Battle"):
    with st.spinner("Battling..."):
        battle_result = run_battle(pokemon1, pokemon2)
        
        if battle_result:
            st.header("Battle Log")
            battle_container = st.container()
            
            if 'logs' in battle_result:
                for log in battle_result['logs']:
                    with battle_container:
                        if isinstance(log, str):
                            st.write(log)
                        elif isinstance(log, dict):
                            attacker = log.get('attacker', 'Unknown')
                            move = log.get('move', 'attack')
                            defender = log.get('defender', 'opponent')
                            damage = log.get('damage', 0)
                            effect = log.get('effect', '')
                            
                            st.write(f"**{attacker}** used **{move}** on **{defender}**")
                            if damage > 0:
                                st.write(f"→ Dealt {damage} damage")
                            if effect:
                                st.write(f"→ Effect: {effect}")
                    
                    time.sleep(1)
            
            if 'winner' in battle_result:
                st.success(f"🎉 **{battle_result['winner'].title()}** wins the battle!")

# Available Pokémon section
st.header("Available Pokémon")
if pokemon_list:
    for pokemon in pokemon_list[:3]:  # Show first 3
        details = get_pokemon_details(pokemon)
        if details:
            with st.expander(f"**{details.get('name', pokemon).title()}**"):
                st.write("Types: " + " / ".join(details.get('types', ['Unknown'])))
                
                if 'stats' in details:
                    st.write("**Stats:**")
                    for stat, value in details['stats'].items():
                        st.write(f"- {stat.title()}: {value}")
                
                if 'moves' in details and details['moves']:
                    st.write("**Moves:**")
                    for move in details['moves'][:3]:  # Show first 3 moves
                        st.write(f"- {move.get('name', 'Unknown')} "
                               f"({move.get('type', '?')}, "
                               f"Power: {move.get('power', '?')})")