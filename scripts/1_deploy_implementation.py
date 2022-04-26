from ape_safe import ApeSafe
from brownie import Contract, YearnRouter, accounts, network

from scripts.utils.constants import get_utils_addresses


def main():
    accounts.clear()
    accounts.load("deployer")

    print("Make sure to run ApeSafe commands in a forked network")
    print(f"You are using the '{network.show_active()}' network")

    utils_addresses = get_utils_addresses()
    implementation_address = utils_addresses["implementation"]

    if not implementation_address:
        safe = ApeSafe(utils_addresses["gnosis_safe"])
        create_call = Contract.from_explorer(utils_addresses["create_call"])

        implementation_bytecode = YearnRouter.deploy.encode_input()
        create_call.performCreate(0, implementation_bytecode, {
                                  "from": safe.account})

        safe_tx = safe.multisend_from_receipts()

        # estimated_gas = safe.estimate_gas(safe_tx)
        # print(f"Estimated gas: {estimated_gas}")

        # safe.preview(safe_tx, call_trace=True)

        safe.post_transaction(safe_tx)

        print(f"Successfully posted tx to Gnosis Safe {safe.account}")

    else:
        print(
            f"YearnRouter has been already deployed at {implementation_address}")
