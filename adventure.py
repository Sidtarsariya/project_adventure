import sys
import json

# Function to load map data from a JSON file
def load_map(filename):
    try:
        with open(filename, 'r') as file:
            map_data = json.load(file)
            return map_data
    except FileNotFoundError:
        sys.stderr.write("Map file '{}' not found.\n".format(filename))
        sys.exit(1)
    except json.JSONDecodeError:
        sys.stderr.write("Invalid JSON format in map file '{}'.\n".format(filename))
        sys.exit(1)

# Function to check if a map is valid
def is_valid_map(map_data):
    if "start" not in map_data or "rooms" not in map_data:
        return False
    room_names = set()
    for room in map_data["rooms"]:
        if "name" not in room or "desc" not in room or "exits" not in room:
            return False
        if room["name"] in room_names:
            return False
        room_names.add(room["name"])
        for exit_direction, exit_room in room["exits"].items():
            if exit_direction not in ["north", "south", "east", "west"]:
                return False
            if exit_room not in room_names:
                return False
    return True

# Function to get information about a room
def get_room_info(room_id, map_data):
    for room in map_data["rooms"]:
        if room["name"] == room_id:
            return room
    return None

# Function to print information about a room
def print_room_info(room_info):
    print("> " + room_info["name"])
    print(room_info["desc"])
    if "items" in room_info:
        print("Items:", ", ".join(room_info["items"]))
    print("Exits:", ", ".join(room_info["exits"]))
    print("What would you like to do?")

# Function to handle the "go" verb
def go(direction, game_state, map_data):
    current_room = game_state["current_room"]
    room_info = get_room_info(current_room, map_data)
    if "exits" in room_info and direction in room_info["exits"]:
        game_state["current_room"] = room_info["exits"][direction]
        room_info = get_room_info(game_state["current_room"], map_data)
        print_room_info(room_info)
    else:
        print("There's no way to go", direction + ".")

# Function to handle the "look" verb
def look(game_state, map_data):
    current_room = game_state["current_room"]
    room_info = get_room_info(current_room, map_data)
    print_room_info(room_info)

# Function to handle the "get" verb
def get_item(item, game_state, map_data):
    current_room = game_state["current_room"]
    room_info = get_room_info(current_room, map_data)
    if "items" in room_info and item in room_info["items"]:
        game_state["inventory"].append(item)
        room_info["items"].remove(item)
        print("You pick up the", item + ".")
    else:
        print("There's no", item, "anywhere.")

# Function to handle the "inventory" verb
def inventory(game_state):
    if not game_state["inventory"]:
        print("You're not carrying anything.")
    else:
        print("Inventory:")
        for item in game_state["inventory"]:
            print(" ", item)

# Function to handle the "quit" verb
def quit_game():
    print("Goodbye!")
    sys.exit(0)

# Function to execute a parsed command
def execute_command(parsed_command, game_state, map_data):
    if len(parsed_command) == 0:
        print("Sorry, I didn't understand that.")
    else:
        verb = parsed_command[0]
        if verb == "go":
            if len(parsed_command) == 1:
                print("Sorry, you need to 'go' somewhere.")
            else:
                go(parsed_command[1], game_state, map_data)
        elif verb == "look":
            look(game_state, map_data)
        elif verb == "get":
            if len(parsed_command) == 1:
                print("Sorry, you need to 'get' something.")
            else:
                get_item(parsed_command[1], game_state, map_data)
        elif verb == "inventory":
            inventory(game_state)
        elif verb == "quit":
            quit_game()
        else:
            print("Sorry, I didn't understand that.")

# Function to parse player input
def parse_input(player_input):
    return player_input.strip().lower().split()

# Main game loop
def game_loop(map_data):
    if not is_valid_map(map_data):
        sys.stderr.write("Invalid map!\n")
        sys.exit(1)

    game_state = {
        "current_room": map_data["start"],
        "inventory": []
    }

    room_info = get_room_info(game_state["current_room"], map_data)
    print_room_info(room_info)

    while True:
        player_input = input().strip()
        parsed_command = parse_input(player_input)
        execute_command(parsed_command, game_state, map_data)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 adventure.py [map filename]\n")
        sys.exit(1)

    map_filename = sys.argv[1]
    map_data = load_map(map_filename)
    game_loop(map_data)
