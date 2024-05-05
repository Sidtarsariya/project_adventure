import sys
import json

# Parse Command-Line Arguments
def parse_arguments():
    if len(sys.argv) != 2:
        print("Usage: python3 adventure.py [map filename]")
        sys.exit(1)
    return sys.argv[1]

# Load and Validate the Map
def load_map(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: Map file '{filename}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in map file '{filename}'.")
        sys.exit(1)

def validate_map(map_data):
    if "start" not in map_data or "rooms" not in map_data:
        print("Error: Map file must contain 'start' and 'rooms' keys.")
        sys.exit(1)
    # Additional validation logic goes here

# Game Engine Functions
def read_input():
    return input("> ")

def parse_command(command):
    return command.strip().lower().split(maxsplit=1)

def execute_command(command, game_state, map_data):
    verb = command[0]
    if verb == "go":
        # Execute the 'go' verb
        go(command[1], game_state, map_data)
    elif verb == "look":
        # Execute the 'look' verb
        look(game_state, map_data)
    elif verb == "get":
        # Execute the 'get' verb
        get(command[1], game_state, map_data)
    elif verb == "inventory":
        # Execute the 'inventory' verb
        inventory(game_state)
    elif verb == "quit":
        # Execute the 'quit' verb
        quit_game()
    elif verb == "help":
        # Execute the 'help' verb
        help_text()
    else:
        print("Error: Unknown command.")

def get_room_info(room_id, map_data):
    for room in map_data["rooms"]:
        if room["name"] == room_id:
            return room

def print_room_info(room_info):
    print(f"> {room_info['name']}\n")
    print(room_info['desc'])
    if "exits" in room_info:
        print("\nExits:", ", ".join(room_info['exits'].keys()))
    if "items" in room_info:
        print("\nItems:", ", ".join(room_info['items']))
    print("\nWhat would you like to do?")

def go(direction, game_state, map_data):
    current_room = game_state["current_room"]
    if direction in map_data["rooms"][current_room]["exits"]:
        game_state["current_room"] = map_data["rooms"][current_room]["exits"][direction]
        room_info = get_room_info(game_state["current_room"], map_data)
        print_room_info(room_info)
    else:
        print("There's no way to go", direction + ".")

def look(game_state, map_data):
    current_room = game_state["current_room"]
    room_info = get_room_info(current_room, map_data)
    print_room_info(room_info)

def get(item_name, game_state, map_data):
    current_room = game_state["current_room"]
    room_info = get_room_info(current_room, map_data)
    if "items" in room_info:
        if item_name in room_info["items"]:
            room_info["items"].remove(item_name)
            game_state["inventory"].append(item_name)
            print(f"You pick up the {item_name}.")
        else:
            print(f"There's no {item_name} here.")
    else:
        print("There are no items here.")

def inventory(game_state):
    if game_state["inventory"]:
        print("Inventory:")
        for item in game_state["inventory"]:
            print(f"  {item}")
    else:
        print("You're not carrying anything.")

def quit_game():
    print("Goodbye!")
    sys.exit(0)

def help_text():
    print("You can run the following commands:")
    print("  go [direction]")
    print("  get [item]")
    print("  look")
    print("  inventory")
    print("  quit")
    print("  help")

# Main Game Loop
def game_loop(map_data):
    current_room = map_data["start"]
    game_state = {
        "current_room": current_room,
        "inventory": []
    }
    while True:
        room_info = get_room_info(current_room, map_data)
        print_room_info(room_info)
        command = read_input()
        parsed_command = parse_command(command)
        execute_command(parsed_command, game_state, map_data)

if __name__ == "__main__":
    map_filename = parse_arguments()
    map_data = load_map(map_filename)
    validate_map(map_data)
    game_loop(map_data)
