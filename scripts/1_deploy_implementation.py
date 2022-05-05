from brownie import YearnRouter, accounts, network

from scripts.utils.constants import set_implementation_address
from scripts.utils.is_fork import is_fork


def main():
    accounts.clear()
    deployer = accounts.load("deployer")

    current_network = network.show_active()
    print(f"You are using the '{current_network}' network")

    yearn_router = YearnRouter.deploy(
        {"from": deployer},
        publish_source=not(is_fork(current_network))
    )
    set_implementation_address(yearn_router.address)
