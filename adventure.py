import json
import sys

class Game:
    def __init__(self, map_filename):
        self.map_filename = map_filename
        self.load_map()
        self.current_room_id = self.map_data["start"]
        self.player_inventory = []

    def load_map(self):
        try:
            with open(self.map_filename, "r") as file:
                self.map_data = json.load(file)
                self.validate_map()
        except FileNotFoundError:
            print("Error: Map file not found.")
            sys.exit(1)
        except json.JSONDecodeError:
            print("Error: Invalid JSON format in map file.")
            sys.exit(1)

    def validate_map(self):
        if "start" not in self.map_data or "rooms" not in self.map_data:
            print("Error: Invalid map file. Missing 'start' or 'rooms' keys.")
            sys.exit(1)
        rooms = set()
        for room in self.map_data["rooms"]:
            if not all(key in room for key in ["name", "desc", "exits"]):
                print("Error: Invalid room object. Missing 'name', 'desc', or 'exits' keys.")
                sys.exit(1)
            if room["name"] in rooms:
                print("Error: Duplicate room names are not allowed.")
                sys.exit(1)
            rooms.add(room["name"])
            for exit_room_id in room["exits"].values():
                if exit_room_id not in rooms:
                    print("Error: Invalid exit room id in exits.")
                    sys.exit(1)

    def print_room_description(self):
        current_room = self.get_current_room()
        print(f"> {current_room['name']}\n")
        print(f"{current_room['desc']}\n")
        print("Exits:", ", ".join(current_room["exits"]))
        if "items" in current_room:
            print("\nItems:", ", ".join(current_room["items"]))
        print("\nWhat would you like to do?")

    def get_current_room(self):
        return self.get_room_by_id(self.current_room_id)

    def get_room_by_id(self, room_id):
        for room in self.map_data["rooms"]:
            if room["name"] == room_id:
                return room
        return None

    def execute_command(self, command):
        parts = command.lower().split()
        if not parts:
            print("Sorry, you need to enter a command.")
            return

        verb = self.match_abbreviation(parts[0], self.get_all_verbs())
        if verb in ["go", "north", "south", "east", "west"]:
            self.go(verb)
        elif verb == "take":
            self.take(" ".join(parts[1:]))
        elif verb == "drop":
            self.drop(" ".join(parts[1:]))
        elif verb == "inventory":
            self.print_inventory()
        elif verb == "help":
            self.print_help()
        else:
            print(f"Sorry, I don't understand the command '{parts[0]}'.")
    
    def match_abbreviation(self, input_str, valid_options):
        matches = [option for option in valid_options if option.startswith(input_str)]
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            print(f"Did you mean {' or '.join(matches)}?")
        return input_str

    def get_all_verbs(self):
        verbs = ["go", "north", "south", "east", "west", "take", "drop", "inventory", "help"]
        return verbs + self.get_room_exits()

    def get_room_exits(self):
        current_room = self.get_current_room()
        return list(current_room["exits"].keys())

    def go(self, direction):
        current_room = self.get_current_room()
        exits = current_room.get("exits", {})
        if direction in exits:
            next_room_id = exits[direction]
            next_room = self.get_room_by_id(next_room_id)
            lock = next_room.get("locked")
            if lock:
                key = next_room.get("key")
                if key not in self.player_inventory:
                    print(f"The door to {next_room['name']} is locked. You need {key} to unlock it.")
                    return
            self.current_room_id = next_room_id
            self.print_room_description()
            self.check_win_or_loss(next_room)
        else:
            print(f"There's no way to go {direction}.")

    def take(self, item):
        current_room = self.get_current_room()
        room_items = current_room.get("items", [])
        if item in room_items:
            self.player_inventory.append(item)
            room_items.remove(item)
            print(f"You take the {item}.")
            self.print_room_description()
        else:
            print(f"There's no {item} here.")

    def drop(self, item):
        if item in self.player_inventory:
            current_room = self.get_current_room()
            current_room_items = current_room.get("items", [])
            current_room_items.append(item)
            self.player_inventory.remove(item)
            print(f"You drop the {item}.")
            self.print_room_description()
        else:
            print(f"You're not carrying {item}.")

    def print_inventory(self):
        if not self.player_inventory:
            print("You're not carrying anything.")
        else:
            print("Inventory:")
            for item in self.player_inventory:
                print("  " + item)

    def print_help(self):
        print("You can run the following commands:")
        print("  go ...")
        print("  take ...")
        print("  drop ...")
        print("  inventory")
        print("  help")

    def check_win_or_loss(self, room):
        if "win_condition" in room:
            condition = room["win_condition"]
            item = condition.get("item")
            if item and item in self.player_inventory:
                print("Congratulations! You win the game!")
                sys.exit(0)
        if "lose_condition" in room:
            condition = room["lose_condition"]
            item = condition.get("item")
            if item and item in self.player_inventory:
                print("You've lost the game. Better luck next time!")
                sys.exit(0)

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
