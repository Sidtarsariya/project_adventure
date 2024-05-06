import json
import sys

class GameEngine:
    def __init__(self, map_file):
        self.map_file = map_file
        self.rooms = {}
        self.current_room = None
        self.inventory = []

    def load_map(self):
        try:
            with open(self.map_file, 'r') as f:
                map_data = json.load(f)
                start_room = map_data.get('start')
                rooms = map_data.get('rooms')
                if not start_room or not rooms:
                    raise ValueError("Invalid map format: 'start' and 'rooms' keys are required.")

                for room_data in rooms:
                    room_id = room_data['name']
                    if room_id in self.rooms:
                        raise ValueError(f"Duplicate room name found: {room_id}")

                    exits = room_data.get('exits', {})
                    for exit_dir, exit_room in exits.items():
                        if exit_room not in [room['name'] for room in rooms]:
                            raise ValueError(f"Invalid exit room '{exit_room}' in room '{room_id}'")
                    
                    self.rooms[room_id] = room_data

                self.current_room = self.rooms[start_room]
        except FileNotFoundError:
            print("Error: Map file not found.", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError:
            print("Error: Invalid JSON format in map file.", file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    def play(self):
        while True:
            self.print_room()
            command = input("What would you like to do? ").strip()
            result = self.parse_command(command)
            if result == 'quit':
                print("Goodbye!")
                break

    def print_room(self):
        print(f"> {self.current_room['name']}\n")
        print(self.current_room['desc'])
        if 'items' in self.current_room:
            print("\nItems:", ", ".join(self.current_room['items']))
        print("\nExits:", ", ".join(self.current_room['exits'].keys()))

    def parse_command(self, command):
        command = command.strip().lower()
        if command == 'quit':
            return 'quit'
        elif command == 'look':
            self.print_room()
        elif command.startswith('go') or command in self.current_room['exits']:
            self.go(command[2:].strip() if command.startswith('go') else command)
        elif command.startswith('get'):
            self.get(command[3:].strip())
        elif command.startswith('drop'):
            self.drop(command[4:].strip())
        elif command.startswith('inv'):
            self.print_inventory()
        elif command == 'help':
            self.print_help()
        else:
            print("Invalid command.")

    def go(self, direction):
        if direction:
            if direction in self.current_room['exits']:
                next_room_id = self.current_room['exits'][direction]
                next_room = self.rooms[next_room_id]
                if 'locked' in next_room and next_room['locked']:
                    if 'unlock_item' in next_room and next_room['unlock_item'] in self.inventory:
                        print(f"You use {next_room['unlock_item']} to unlock the door.")
                        next_room['locked'] = False
                        self.current_room = next_room
                        self.print_room()
                    else:
                        print("The door is locked.")
                else:
                    self.current_room = next_room
                    self.print_room()
            else:
                print(f"There's no way to go {direction}.")
        else:
            print("Sorry, you need to 'go' somewhere.")

    def get(self, item):
        if not item:
            print("Sorry, you need to 'get' something.")
        elif 'items' in self.current_room and item in self.current_room['items']:
            self.inventory.append(item)
            self.current_room['items'].remove(item)
            print(f"You pick up the {item}.")
        else:
            print(f"There's no {item} anywhere.")

    def drop(self, item):
        if not item:
            print("Sorry, you need to 'drop' something.")
        elif item in self.inventory:
            self.current_room['items'].append(item)
            self.inventory.remove(item)
            print(f"You drop the {item}.")
        else:
            print(f"You don't have {item} in your inventory.")

    def print_inventory(self):
        if self.inventory:
            print("Inventory:")
            for item in self.inventory:
                print(f"  {item}")
        else:
            print("You're not carrying anything.")

    def print_help(self):
        valid_verbs = sorted(['go', 'get', 'drop', 'look', 'inventory', 'quit', 'help'])
        print("You can run the following commands:")
        for verb in valid_verbs:
            print(f"  {verb} ...")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python adventure.py <map_file>", file=sys.stderr)
        sys.exit(1)

    map_file = sys.argv[1]
    game = GameEngine(map_file)
    game.load_map()
    game.play()
