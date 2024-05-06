import sys
import json

def load_map(map_file):
    with open(map_file) as f:
        map_data = json.load(f)

    # Check if the map is valid
    if 'start' not in map_data or 'rooms' not in map_data:
        raise ValueError("Missing 'start' or 'rooms' in the map file.")

    start_room = map_data['start']
    rooms = map_data['rooms']

    room_names = {room['name']: room for room in rooms}
    if len(room_names) != len(rooms):
        raise ValueError("Room names must be unique.")

    for room in rooms:
        if 'exits' in room:
            for direction, room_name in room['exits'].items():
                if room_name not in room_names:
                    raise ValueError(f"Invalid room name '{room_name}' in exit direction '{direction}'.")

    return start_room, rooms, room_names


def display_room(room, exits, inventory):
    print(f"> {room['name']}")
    print(room['desc'])
    print("\nExits:", ', '.join(exits))
    print("\nInventory:", ', '.join(inventory))
    print("\nWhat would you like to do?")


def handle_input(command, room_names, inventory):
    words = command.lower().split()

    if len(words) == 0:
        return None

    verb = words[0]

    if verb == 'go':
        direction = words[1]
        if direction in room_names[room]['exits']:
            return 'go', direction
        else:
            print(f"There's no way to go {direction}.")

    elif verb == 'look':
        return None

    elif verb == 'inventory' or verb == 'i':
        return None

    elif verb == 'get':
        if len(words) > 1:
            item = words[1]
            if item in room_names[room]['items']:
                room_names[room]['items'].remove(item)
                inventory.append(item)
                return 'get', item
            else:
                print(f"There's no {item} here.")
        else:
            print("Get what?")

    elif verb == 'quit' or verb == 'q':
        return 'quit'

    else:
        print(f"I don't understand '{verb}'.")

    return None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python adventure.py [map filename]")
        sys.exit(1)

    map_file = sys.argv[1]

    try:
        room, rooms, room_names = load_map(map_file)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    exits = list(room_names[room]['exits'].keys())
    inventory = []

    while True:
        display_room(room_names[room], exits, inventory)
        command = input()
        action, arg = handle_input(command, room_names, inventory)

        if action == 'go':
            room = room_names[room['exits'][arg]]
            exits = list(room_names[room]['exits'].keys())
        elif action == 'get':
            room_names[room]['items'].remove(arg)
        elif action == 'quit':
            print("Goodbye!")
            sys.exit(0)