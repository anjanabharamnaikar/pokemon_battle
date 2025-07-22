# Pokémon Battle MCP Server

This project is a Model Context Protocol (MCP) server for simulating Pokémon battles and providing Pokémon data via a REST API. It features a FastAPI backend, a frontend (see `frontend/app.py`), and integration with a language model for advanced interactions.

## Features

- **Pokémon Data API**: Query stats, moves, and types for various Pokémon.
- **Battle Simulation**: Simulate turn-based battles between two Pokémon, including move selection, type effectiveness, and battle logs.
- **LLM Integration**: Interact with a language model for Pokémon-related queries.
- **Extensible MCP Server**: Register resources and tools for future expansion.

## Project Structure

```
pokemon-battle-mcp-server/
├── backend/
│   ├── __init__.py
│   ├── battle_simulator.py
│   ├── local_mcp.py
│   ├── mcp_server.py         # Main FastAPI server and MCP logic
│   ├── pokemon_data.py
│   ├── data/
│   │   └── pokemon_data.json # Pokémon stats, moves, and types
├── frontend/
│   └── app.py                # Frontend application (see for UI)
├── requirements.txt          # Python dependencies
├── test.py                   # Test script
└── README.md                 # Project documentation
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repo-url>
cd pokemon-battle-mcp-server
```

### 2. Create and Activate a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Server

```bash
python backend/mcp_server.py
```
The server will start at `http://localhost:8001`.

## API Endpoints

### Health Check

- `GET /`
  - Returns server status.

### List All Pokémon

- `GET /pokemon`
  - Returns a list of all available Pokémon names.

### Get Pokémon Details

- `GET /pokemon/{name}`
  - Returns stats, moves, and types for the specified Pokémon.
  - Example: `GET /pokemon/pikachu`

### Simulate a Battle

- `POST /battle/simulate`
  - Request Body:
    ```json
    {
      "pokemon1": "pikachu",
      "pokemon2": "bulbasaur"
    }
    ```
  - Response:
    ```json
    {
      "winner": "pikachu",
      "logs": ["..."],
      "hp_remaining": {
        "Pikachu": 12,
        "Bulbasaur": 0
      }
    }
    ```

### LLM Interaction

- `POST /llm/interact`
  - Request Body:
    ```json
    {
      "prompt": "Who is stronger, Charizard or Blastoise?"
    }
    ```
  - Response:
    ```json
    {
      "response": "Charizard has a type advantage against..."
    }
    ```

## Customization & Extensibility

- Add new Pokémon to `backend/data/pokemon_data.json`.
- Extend battle logic in `backend/battle_simulator.py`.
- Register new resources/tools in `backend/mcp_server.py`.

## Frontend


The frontend is located in `frontend/app.py` and is built using Streamlit. You can use it to interact with the backend APIs via a simple web interface.

### Running the Frontend

First, ensure you have Streamlit installed:

```bash
pip install streamlit
```

Then, run the frontend app:

```bash
streamlit run frontend/app.py
```

This will start the Streamlit app, usually at `http://localhost:8501`, where you can access the UI for Pokémon battles and data queries.



## Requirements

- Python 3.8+
- FastAPI
- Uvicorn
- Transformers
- Pydantic
- python-dotenv

See `requirements.txt` for the full list.

## License

MIT License

## Acknowledgements

- Pokémon data and images © Nintendo, Game Freak, The Pokémon Company.
- Language model via HuggingFace Transformers.
