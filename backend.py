# backend.py
import requests
import os
import json
import yaml
from typing import Iterator, Any, TypedDict
from colorama import Fore, init

init(autoreset=True)

class Message(TypedDict):
    role: str
    content: str

OLLAMA_BASE_URL = "http://localhost:11434"

# Instead of using argparse here, you might consider passing the config path directly 
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "sample_story.yaml")
 # Update with your actual path

with open(CONFIG_PATH, 'r') as f:
    config = yaml.safe_load(f)

MODEL = config.get('model', 'llama3')
NUM_CTX = config.get('num_tokens', 6000)
# TEMPERATURE = config.get('temperature', 0.5)
STORY_CARD = config.get('story_card')

messages = []

def _build_story_system_prompt(story_card: str) -> tuple[str, str]:
    story_system_prompt = """
I want you to embody the essence of a classic text adventure game narrator, guiding the player through a game that follows the story of the mutiny of the HMS Bounty, 
without breaking character or referring to yourself. The game is crafted with a trial narrative structure, designed to offer branching choices that 
merge back into the main storyline.

Within the game, every location should be described with at least three sentences, immersing the player in the game setting. 
The player manages an inventory, which plays a crucial role in navigating the game's challenges.

Start by introducing the first room in detail, setting the scene for the player. Present choices in the game as numbered options (e.g., 1, 2, 3, 4), 
allowing the player to select a path by typing the corresponding number. These choices will lead to various trials, each with its distinct narrative 
branch that loops back to the main story.

After the initial description, prompt the player with a set of options for actions or directions to explore. These options should clearly impact the 
game's progression and lead to tangible consequences within the narrative's scope. Always describe the outcome of the player's actions and adapt 
the story based on their choices.

Conclude the game in 15 to 20 turns when the narrative reaches a natural endpoint.

Lastly, before starting the interactive portion, generate a preamble that introduces the player to the world of the game.
    """
    start_message = f"""
Use the following story card between triple ticks to learn the story and what happened so far - this will serve to guide you as you develop each prompt:

{story_card}

Now, generate initial description of the story and the player's surroundings. Provide only the initial description of the story
and the player's surroundings.
    """
    return story_system_prompt, start_message

def truncate_messages(messages, max_tokens):
    if not messages or len(messages) < 2:
        return
    token_counts = [len(message['content'].split()) for message in messages]
    current_total_count = sum(token_counts)
    index = 1
    while current_total_count > max_tokens and len(messages) > 2:
        messages.pop(1)
        current_total_count -= token_counts[index]
        index += 1

def _stream_llm_chat(model: str, message: str) -> Iterator[Any]:
    messages.append({"role": "user", "content": message})
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": {
            "num_ctx": NUM_CTX,
            "temperature": TEMPERATURE,
        },
    }
    for token in requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, stream=True).iter_lines():
        jsonstr = json.loads(token)
        yield jsonstr["message"]["content"]

def reset_game(mode="story"):
    global messages, TEMPERATURE
    if mode == "forge":
        TEMPERATURE = 0.8  # High temperature for creative, less predictable responses
    else:
        TEMPERATURE = 0.2  # Low temperature for more deterministic storytelling

    messages.clear()
    system_prompt, first_message = _build_story_system_prompt(STORY_CARD)
    messages.append({"role": "system", "content": system_prompt})
    response_message = ""
    for token in _stream_llm_chat(MODEL, first_message):
        response_message += token
    messages.append({"role": "assistant", "content": response_message})
    return response_message

def process_command(user_input: str) -> str:
    global messages
    messages.append({"role": "user", "content": user_input})
    truncate_messages(messages, NUM_CTX)
    response_message = ""
    for token in _stream_llm_chat(MODEL, user_input):
        response_message += token
    messages.append({"role": "assistant", "content": response_message})
    return response_message

def undo_last_turn() -> str:
    global messages
    # Ensure there's at least one turn to undo (skip the system prompt)
    if len(messages) > 2:
        # Remove last assistant message and the preceding user message
        messages.pop()  # Remove the last assistant message
        messages.pop()  # Remove the last user message

    # Reconstruct the narrative from the remaining assistant messages
    narrative = ""
    for msg in messages:
        if msg["role"] == "assistant":
            narrative += msg["content"] + "\n\n"
    return narrative.strip()

if __name__ == "__main__":
    print(reset_game())
    while True:
        user_input = input("> ")
        if user_input.lower() in ["quit", "exit"]:
            break
        print(process_command(user_input))
