import json
import sys

class Room:
    def __init__(self, name, desc, exits, items=None, locked=False, key=None, win_condition=None, lose_condition=None):
        self.name = name
        self.desc = desc
        self.exits = exits
        self.items = items if items else []
        self.locked = locked
        self.key = key
        self.win_condition = win_condition
        self.lose_condition = lose_condition

class Game:
    def __init__(self, map_file):
        self.rooms = {}
        self.current_room = None
        self.load_map(map_file)

    def load_map(self, map_file):
        try:
            with open(map_file, 'r') as file:
                data = json.load(file)
                self.validate_map(data)
                self.create_rooms(data['rooms'])
                start_room_name = data['start']
                self.current_room = self.rooms[start_room_name]
        except FileNotFoundError:
            print("Error: Map file not found.")
            sys.exit(1)
        except json.JSONDecodeError:
            print("Error: Invalid JSON format in map file.")
            sys.exit(1)
        except Exception as e:
            print("Error:", e)
            sys.exit(1)

    def validate_map(self, data):
        start_room = data.get('start')
        rooms = data.get('rooms')

        if not start_room or not rooms:
            raise ValueError("Map file must contain 'start' and 'rooms' keys.")
        
        room_names = set()
        for room in rooms:
            name = room.get('name')
            if not name:
                raise ValueError("Room must have a 'name' field.")
            if name in room_names:
                raise ValueError("Room names must be unique.")
            room_names.add(name)

            exits = room.get('exits')
            if not exits or not isinstance(exits, dict):
                raise ValueError("Room must have 'exits' field as a dictionary.")
            for exit_direction, exit_room in exits.items():
                if exit_room not in room_names:
                    raise ValueError("Invalid exit room id in exits.")

    def create_rooms(self, rooms_data):
        for room_data in rooms_data:
            name = room_data['name']
            desc = room_data['desc']
            exits = room_data['exits']
            items = room_data.get('items')
            locked = room_data.get('locked', False)
            key = room_data.get('key')
            win_condition = room_data.get('win_condition')
            lose_condition = room_data.get('lose_condition')
            self.rooms[name] = Room(name, desc, exits, items, locked, key, win_condition, lose_condition)

    def print_room_description(self):
        print(f"> {self.current_room.name}\n\n{self.current_room.desc}\n")
        exits = ", ".join(self.current_room.exits.keys())
        print(f"Exits: {exits}\n")

    def execute_command(self, command):
        if command == "":
            print("Sorry, you need to enter a command.")
            return

        tokens = command.lower().split()
        verb = tokens[0]

        if verb == "go":
            if len(tokens) < 2:
                print("Sorry, you need to specify a direction to go.")
                return
            direction = tokens[1]
            self.go(direction)
        elif verb == "look":
            self.print_room_description()
        elif verb == "inventory":
            self.print_inventory()
        elif verb == "quit":
            print("Goodbye!")
            sys.exit(0)
        elif verb == "get":
            if len(tokens) < 2:
                print("Sorry, you need to specify an item to get.")
                return
            item_name = " ".join(tokens[1:])
            self.get_item(item_name)
        elif verb == "drop":
            if len(tokens) < 2:
                print("Sorry, you need to specify an item to drop.")
                return
            item_name = " ".join(tokens[1:])
            self.drop_item(item_name)
        else:
            print(f"Sorry, I don't understand the command '{command}'.")

    def go(self, direction):
        if direction in self.current_room.exits:
            next_room_name = self.current_room.exits[direction]
            if next_room_name in self.rooms:
                self.current_room = self.rooms[next_room_name]
                self.print_room_description()
            else:
                print("Error: Invalid exit room ID.")
        else:
            print(f"There's no way to go {direction}.")

    def print_inventory(self):
        if not self.current_room.items:
            print("You're not carrying anything.")
        else:
            print("Inventory:")
            for item in self.current_room.items:
                print(f"  {item}")

    def get_item(self, item_name):
        if item_name in self.current_room.items:
            self.current_room.items.remove(item_name)
            print(f"You pick up the {item_name}.")
        else:
            print(f"There's no {item_name} here.")

    def drop_item(self, item_name):
        self.current_room.items.append(item_name)
        print(f"You drop the {item_name}.")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 adventure.py [map filename]")
        sys.exit(1)
    
    game = Game(sys.argv[1])
    game.print_room_description()

    while True:
        command = input("> ").strip()
        game.execute_command(command)

if __name__ == "__main__":
    main()
