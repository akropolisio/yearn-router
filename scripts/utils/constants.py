import json

from brownie import chain


def get_utils_path():
    return f"addresses/{chain.id}.json"


def get_utils_addresses():
    with open(get_utils_path(), "r", encoding="utf-8") as file:
        return json.load(file)


def set_utility_address(key, value):
    with open(get_utils_path(), "r+", encoding="utf-8") as file:
        data = json.load(file)

        data[key] = value

        file.seek(0)
        json.dump(data, file, indent=2)
