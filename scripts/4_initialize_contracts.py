from ape_safe import ApeSafe
from brownie import ZERO_ADDRESS, YearnRouter, accounts

from scripts.utils.constants import get_utils_addresses


def main():
    accounts.clear()
    accounts.load("deployer")

    utils_addresses = get_utils_addresses()

    safe = ApeSafe(utils_addresses["gnosis_safe"])
    registry_address = utils_addresses["vault_registry"]
    implementation_address = utils_addresses["implementation"]
    proxy_address = utils_addresses["proxy"]

    yearn_router = YearnRouter.at(implementation_address)
    if yearn_router.owner() == ZERO_ADDRESS:
        yearn_router.initialize(registry_address, {"from": safe.account})

    proxied_yearn_router = YearnRouter.at(proxy_address)
    if proxied_yearn_router.owner() == ZERO_ADDRESS:
        proxied_yearn_router.initialize(
            registry_address, {"from": safe.account})

    safe_tx = safe.multisend_from_receipts()

    # estimated_gas = safe.estimate_gas(safe_tx)
    # print(f"Estimated gas: {estimated_gas}")

    # safe.preview(safe_tx, call_trace=True)

    safe.post_transaction(safe_tx)

    print(f"Successfully posted tx to Gnosis Safe {safe.account}")
