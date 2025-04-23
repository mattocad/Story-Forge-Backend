# Story Forge – Backend

Story Forge is an interactive fiction platform that transforms traditional storybooks into AI-powered text-adventure games using local large language models (LLMs). This backend, built with FastAPI, handles narrative generation by querying local models through the Ollama framework.

## Features

- FastAPI server with RESTful endpoints
- Local LLM integration (tested with LLaMA 2 and 3 via Ollama)
- Structured narrative control using YAML-based "Story Cards"
- Adjustable model temperature to toggle narrative strictness
- Session restart, input handling, and export functionality

## Requirements

- Python 3.10 or higher
- [Ollama](https://ollama.com/) installed locally and running a supported model
- pip packages listed in `requirements.txt`

## Installation

git clone https://github.com/yourusername/storyforge-backend.git
cd storyforge-backend
pip install -r requirements.txt
Running the Server
bash
Copy
Edit
uvicorn main:app --reload
This starts the backend on http://localhost:8000.

API Endpoints
POST /start: Initializes a new game session

POST /choice: Submits a player decision (e.g., "1", "2", "3")

POST /restart: Resets the current session

GET /export: Returns the session transcript as plain text

## Project Structure
graphql
Copy
Edit
storyforge-backend/
├── main.py                # FastAPI app and routing
├── prompts/
│   └── system_prompt.txt  # Base prompt for initializing gameplay
├── models/
│   └── story_card.yaml    # Narrative structure and event guide
├── utils/
│   └── game_loop.py       # Core interaction logic
└── requirements.txt

## Notes
Story Cards guide AI output to maintain consistency with the original narrative.

Responses are turn-based and triggered by numerical choices.

Backend was tested with llama3:8b and performs best with a context window over 8,000 tokens.

## License
Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
© 2025 Matthew Nazarian
