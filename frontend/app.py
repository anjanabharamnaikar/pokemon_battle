import streamlit as st
import requests

# -------------------------
# Configuration
# -------------------------
BACKEND_URL = "http://127.0.0.1:8001"
st.set_page_config(page_title="Pokémon Battle Arena", page_icon="⚡")

# -------------------------
# Helper Functions
# -------------------------

def fetch_pokemon_list():
    """Fetches the list of available Pokémon from the backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/pokemon")
        response.raise_for_status()
        return response.json().get("pokemon", [])
    except Exception as e:
        st.error(f"Failed to fetch Pokémon list: {e}")
        return []

def simulate_battle(pokemon1, pokemon2):
    """Simulates a battle between two Pokémon using the backend"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/battle/simulate",
            json={"pokemon1": pokemon1, "pokemon2": pokemon2}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Battle failed: {e}")
        return None

def ask_llm(prompt):
    """Sends user prompt to LLM endpoint and returns the response"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/llm/interact",
            json={"prompt": prompt}
        )
        response.raise_for_status()
        return response.json().get("response", "Sorry, I couldn't process that.")
    except Exception as e:
        return f"Error contacting LLM: {e}"

# -------------------------
# LLM Chat Interface
# -------------------------

st.title("⚡ Pokémon Battle Arena")
st.header("🔍 Pokémon Battle Assistant")

# Initialize chat state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Ask about Pokémon or request a battle"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        reply = ask_llm(prompt)
        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

# -------------------------
# Direct Battle Simulation
# -------------------------

st.header("⚔️ Direct Battle Simulation")

pokemon_list = fetch_pokemon_list()

if pokemon_list:
    col1, col2 = st.columns(2)

    with col1:
        pokemon1 = st.selectbox("First Pokémon", pokemon_list, key="poke1")

    with col2:
        pokemon2 = st.selectbox("Second Pokémon", pokemon_list, key="poke2")

    if st.button("Start Battle"):
        with st.spinner("Battling..."):
            try:
                response = simulate_battle(pokemon1, pokemon2)

                if response is None:
                    st.error("No response received from battle engine.")
                elif "error" in response:
                    st.error(response["error"])
                else:
                    st.subheader("📜 Battle Log")
                    for log in response.get("logs", []):
                        st.write(f"• {log}")

                    st.success(f"🏆 Winner: {response['winner'].capitalize()}")

                    if "hp_remaining" in response:
                        st.markdown("### ❤️ HP Remaining")
                        st.json(response["hp_remaining"])

            except Exception as e:
                st.error(f"Battle failed: {str(e)}")
