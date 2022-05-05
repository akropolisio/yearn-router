from brownie import network
from brownie._config import CONFIG


def is_fork():
    network_config = CONFIG.networks[network.show_active()]
    return "cmd_settings" in network_config and "fork" in network_config["cmd_settings"]
