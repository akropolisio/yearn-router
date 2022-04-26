from brownie import UtilProxy, UtilProxyAdmin, YearnRouter
from eth_utils import is_checksum_address

from scripts.utils.constants import get_utils_addresses, set_utility_address
from scripts.utils.publish_sources import publish_sources


def main():
    utils_addresses = get_utils_addresses()

    proxy_address = utils_addresses["proxy"]
    implementation_address = utils_addresses["implementation"]
    proxy_admin_address = utils_addresses["proxy_admin"]

    if not proxy_address:
        proxy_address = input("Enter Proxy contract address: ")
        if not is_checksum_address(proxy_address):
            print(f"Invalid address: {proxy_address}")
            return

        set_utility_address("proxy", proxy_address)

    publish_sources(UtilProxy, proxy_address)
    publish_sources(YearnRouter, implementation_address)
    publish_sources(UtilProxyAdmin, proxy_admin_address)
