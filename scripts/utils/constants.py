import json

from brownie import chain, network


def get_utils_path():
    is_fork = network.show_active().endswith("fork")
    if is_fork:
        return "addresses/fork.json"
    return f"addresses/{chain.id}.json"


def get_utils_addresses():
    with open(get_utils_path(), "r", encoding="utf-8") as file:
        return json.load(file)


def set_proxy_admin_address(address):
    set_utility_address("proxy_admin", address)


def set_implementation_address(address):
    utils_addresses = get_utils_addresses()
    implementation_addresses = utils_addresses["implementations"]
    implementation_addresses.append(address)

    set_utility_address("implementations", implementation_addresses)


def set_proxy_address(address):
    set_utility_address("proxy", address)


def clear_utils_addresses():
    utils_addresses = get_utils_addresses()
    proxy_address = utils_addresses["proxy"]
    proxy_admin_address = utils_addresses["proxy_admin"]
    implementations = utils_addresses["implementations"]

    is_empty = not(proxy_address) and not(
        proxy_admin_address) and len(implementations) == 0

    if is_empty:
        return

    is_fork = network.show_active().endswith("fork")
    if not is_fork:
        confirmation = input(
            "!!! This will remove contract addresses. Type 'yes' to confirm: ")
        if confirmation != "yes":
            return
    set_utility_address("proxy_admin", None)
    set_utility_address("proxy", None)
    set_utility_address("implementations", [])


def set_utility_address(key, value):
    with open(get_utils_path(), "r+", encoding="utf-8") as file:
        data = json.load(file)

        data[key] = value

        file.seek(0)
        json.dump(data, file, indent=2)
        file.truncate()
        file.close()
