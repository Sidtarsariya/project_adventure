def main():
    if len(sys.argv) != 2:
        print("Usage: python3 adventure.py [map_filename]")
        sys.exit(1)

    map_filename = sys.argv[1]
    map_data = load_map(map_filename)
    validate_map(map_data)

    current_room = map_data["start"]
    rooms = {room["name"]: room for room in map_data["rooms"]}
    inventory = []

    verbs = {
        "go": "go",
        "look": "look",
        "get": "get",
        "inventory": "inventory",
        "quit": "quit",
        "help": "help"
    }

    while True:
        room = rooms[current_room]
        print(f"> {room['name']}\n\n{room['desc']}\n")
        print("Exits:", ", ".join(room["exits"]))
        print("Inventory:", ", ".join(inventory) if inventory else "Empty")
        command = input("\nWhat would you like to do? ").strip().lower()

        # Abbreviations handling
        command_parts = command.split()
        verb = command_parts[0]
        if verb in verbs:
            verb = verbs[verb]
        else:
            print("Invalid command. Type 'help' to see valid commands.")
            continue

        if verb == "go":
            direction = " ".join(command_parts[1:])
            if direction in room["exits"]:
                current_room = room["exits"][direction]
            else:
                print("There's no way to go", direction + ".")
        elif verb == "look":
            print(f"\n> {room['name']}\n\n{room['desc']}\n")
        elif verb == "get":
            item = " ".join(command_parts[1:])
            if item in room.get("items", []):
                inventory.append(item)
                room["items"].remove(item)
                print(f"You pick up the {item}.")
            else:
                print(f"There's no {item} anywhere.")
        elif verb == "drop":
            item = " ".join(command_parts[1:])
            if item in inventory:
                inventory.remove(item)
                room["items"].append(item)
                print(f"You drop the {item}.")
            else:
                print(f"You're not carrying {item}.")
        elif verb == "inventory":
            print("\nInventory:", ", ".join(inventory) if inventory else "Empty")
        elif verb == "quit":
            print("Goodbye!")
            sys.exit()
        elif verb == "help":
            print("\nYou can run the following commands:")
            print("  " + ", ".join(verbs.keys()))
            print("\nYou can also use exit directions as verbs.")
        else:
            print("Sorry, I don't understand that command.")

if __name__ == "__main__":
    main()
