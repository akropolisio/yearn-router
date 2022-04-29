from brownie import UtilProxy, YearnRouter, accounts, network

from scripts.utils.constants import get_utils_addresses, set_proxy_address
from scripts.utils.get_proxied_implementation import get_proxied_implementation


def main():
    accounts.clear()
    deployer = accounts.load("deployer")

    current_network = network.show_active()
    is_fork = current_network.endswith("fork")
    print(f"You are using the '{current_network}' network")

    utils_addresses = get_utils_addresses()
    implementation_address = utils_addresses["implementations"][-1]
    proxy_admin_address = utils_addresses["proxy_admin"]
    registry_address = utils_addresses["vault_registry"]
    proxy_address = utils_addresses["proxy"]

    print(f"Using YearnRouter address {implementation_address}")

    if not proxy_address:
        yearn_router = YearnRouter.at(implementation_address)
        initializer = yearn_router.initialize.encode_input(registry_address)
        proxy = UtilProxy.deploy(
            implementation_address,
            proxy_admin_address,
            initializer,
            {"from": deployer},
            publish_source=not(is_fork)
        )
        proxy_address = proxy.address
        set_proxy_address(proxy_address)

        gnosis_safe_address = utils_addresses["gnosis_safe"]
        yearn_router = get_proxied_implementation(
            YearnRouter, "YearnRouter", proxy_address)
        yearn_router.transferOwnership(gnosis_safe_address, {"from": deployer})
        print(
            f"Transferred Proxy implementation ownership from {deployer} to {gnosis_safe_address}")

    else:
        print(
            f"Proxy has been already deployed at {proxy_address}")
