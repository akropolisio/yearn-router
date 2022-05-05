from brownie import UtilProxyAdmin, accounts, network

from scripts.utils.constants import clear_utils_addresses, get_utils_addresses, set_proxy_admin_address
from scripts.utils.is_fork import is_fork


def main():
    print(f"You are using the '{network.show_active()}' network")

    accounts.clear()
    deployer = accounts.load("deployer")

    if is_fork():
        clear_utils_addresses()

    utils_addresses = get_utils_addresses()

    proxy_admin_address = utils_addresses["proxy_admin"]

    if not proxy_admin_address:
        proxy_admin = UtilProxyAdmin.deploy(
            {"from": deployer},
            publish_source=not(is_fork())
        )
        proxy_admin_address = proxy_admin.address
        set_proxy_admin_address(proxy_admin_address)

        gnosis_safe_address = utils_addresses["gnosis_safe"]
        proxy_admin.transferOwnership(gnosis_safe_address, {"from": deployer})
        print(
            f"Transferred Proxy Admin ownership from {deployer} to {gnosis_safe_address}")

    print(f"Proxy Admin deployed at {proxy_admin_address}")
    proxy_admin = UtilProxyAdmin.at(proxy_admin_address)
    print(f"Owner: {proxy_admin.owner()}")
