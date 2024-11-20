import json
import os

program_number_file = "program_number.json"

def get_program_number():
    if os.path.exists(program_number_file):
        with open(program_number_file, 'r') as file:
            data = json.load(file)
            return data.get("program_number", 1)  # Default to 1 if not found
    else:
        return 1

def increment_program_number():
    program_number = get_program_number() + 1
    with open(program_number_file, 'w') as file:
        json.dump({"program_number": program_number}, file)
    return program_number

def reset_program_number(value=1):
    with open(program_number_file, 'w') as file:
        json.dump({"program_number": value}, file)
    print(f"Program number reset to {value}.")
