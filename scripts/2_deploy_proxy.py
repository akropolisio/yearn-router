from ape_safe import ApeSafe
from brownie import Contract, UtilProxy, accounts, network
from eth_utils import is_checksum_address

from scripts.utils.constants import get_utils_addresses, set_utility_address


def main():
    accounts.clear()
    accounts.load("deployer")

    print("Make sure to run ApeSafe commands in a forked network")
    print(f"You are using the '{network.show_active()}' network")

    utils_addresses = get_utils_addresses()
    implementation_address = utils_addresses["implementation"]
    proxy_address = utils_addresses["proxy"]

    if not implementation_address:
        implementation_address = input("Enter YearnRouter contract address: ")

        if not is_checksum_address(implementation_address):
            print(f"Invalid address: {implementation_address}")
            return

        set_utility_address("implementation", implementation_address)

    print(f"Using YearnRouter address {implementation_address}")

    if not proxy_address:
        safe = ApeSafe(utils_addresses["gnosis_safe"])
        create_call = Contract.from_explorer(utils_addresses["create_call"])

        proxy_admin_address = utils_addresses["proxy_admin"]

        initialize_data = b""
        proxy_bytecode = UtilProxy.deploy.encode_input(
            implementation_address, proxy_admin_address, initialize_data)
        create_call.performCreate(0, proxy_bytecode, {"from": safe.account})

        safe_tx = safe.multisend_from_receipts()

        # estimated_gas = safe.estimate_gas(safe_tx)
        # print(f"Estimated gas: {estimated_gas}")

        # safe.preview(safe_tx, call_trace=True)

        safe.post_transaction(safe_tx)

        print(f"Successfully posted tx to Gnosis Safe {safe.account}")
    else:
        print(
            f"Proxy has been already deployed at {proxy_address}")
