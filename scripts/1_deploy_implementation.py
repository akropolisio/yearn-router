from brownie import YearnRouter, accounts, network

from scripts.utils.constants import set_implementation_address
from scripts.utils.is_fork import is_fork


def main():
    print(f"You are using the '{network.show_active()}' network")

    accounts.clear()
    deployer = accounts.load("deployer")

    yearn_router = YearnRouter.deploy(
        {"from": deployer},
        publish_source=not(is_fork())
    )
    set_implementation_address(yearn_router.address)
