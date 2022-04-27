from brownie import YearnRouter, accounts, network

from scripts.utils.constants import set_implementation_address


def main():
    accounts.clear()
    deployer = accounts.load("deployer")

    current_network = network.show_active()
    is_fork = current_network.endswith("fork")
    print(f"You are using the '{current_network}' network")

    yearn_router = YearnRouter.deploy(
        {"from": deployer},
        publish_source=not(is_fork)
    )
    set_implementation_address(yearn_router.address)
