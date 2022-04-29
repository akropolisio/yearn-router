import brownie
import pytest

AMOUNT = 100


def test_config_live(live_token, live_vault, live_registry, live_yearn_router, interface):
    assert live_registry.numVaults(live_token) > 0
    assert interface.RegistryAPI(
        live_yearn_router.registry()).latestVault(live_token) == live_vault
    assert interface.RegistryAPI(
        live_yearn_router.registry()).numVaults(live_token) == 1
    assert interface.RegistryAPI(live_yearn_router.registry()).vaults(
        live_token, 0) == live_vault
    assert live_yearn_router.latestVault(live_token) == live_vault
    assert live_yearn_router.numVaults(live_token) == 1
    assert live_yearn_router.vaults(live_token, 0) == live_vault


def test_setRegistry_live(
    random_address, owner, live_gov, live_yearn_router, new_registry, gov
):
    with brownie.reverts():
        live_yearn_router.setRegistry(random_address, {"from": random_address})

    # Cannot set to an invalid registry
    with brownie.reverts():
        live_yearn_router.setRegistry(random_address, {"from": owner})

    with brownie.reverts():
        live_yearn_router.setRegistry(random_address, {"from": live_gov})

    # yGov must be the gov on the new registry too
    new_registry.setGovernance(random_address, {"from": gov})
    new_registry.acceptGovernance({"from": random_address})
    with brownie.reverts():
        live_yearn_router.setRegistry(new_registry, {"from": owner})
    new_registry.setGovernance(live_gov, {"from": random_address})
    new_registry.acceptGovernance({"from": live_gov})

    live_yearn_router.setRegistry(new_registry, {"from": owner})


def test_transfer_ownership_live(random_address, owner, live_yearn_router, new_registry, gov, live_gov):
    assert live_yearn_router.owner() == owner
    new_registry.setGovernance(live_gov, {"from": gov})
    new_registry.acceptGovernance({"from": live_gov})

    with brownie.reverts():
        live_yearn_router.setRegistry(random_address, {"from": random_address})

    with brownie.reverts():
        live_yearn_router.transferOwnership(
            random_address, {"from": random_address})

    live_yearn_router.transferOwnership(random_address, {"from": owner})

    # new owner can set registry
    assert live_yearn_router.owner() == random_address
    live_yearn_router.setRegistry(new_registry, {"from": random_address})


def test_deposit_live(live_token, live_vault, live_yearn_router, live_vault_user, random_address):
    live_token.transfer(random_address, 10000, {"from": live_vault_user})
    assert live_token.balanceOf(
        live_yearn_router) == live_vault.balanceOf(random_address) == 0

    live_token.approve(live_yearn_router, 10000, {"from": random_address})
    live_yearn_router.deposit(live_token, random_address, 10000, {
                              "from": random_address})
    expectedBalance = (10000 / live_vault.pricePerShare()) * \
        (10**live_vault.decimals())

    assert live_vault.balanceOf(live_yearn_router) == 0
    assert live_token.balanceOf(live_yearn_router) == 0
    assert live_token.balanceOf(random_address) == 0
    assert live_vault.balanceOf(random_address) == expectedBalance


def test_deposit_with_recipient_live(live_token, live_vault, live_yearn_router, live_vault_user, random_address, random_address_2):
    live_token.transfer(random_address, 10000, {"from": live_vault_user})
    live_token.approve(live_yearn_router, 10000, {"from": random_address})
    expectedBalance = (10000 / live_vault.pricePerShare()) * \
        (10**live_vault.decimals())
    live_yearn_router.deposit(live_token, random_address_2, 10000, {
                              "from": random_address})

    assert live_vault.balanceOf(live_yearn_router) == 0
    assert live_token.balanceOf(live_yearn_router) == 0
    assert live_token.balanceOf(random_address) == 0
    assert live_vault.balanceOf(random_address) == 0
    assert live_vault.balanceOf(random_address_2) == expectedBalance


def test_withdraw_live(live_token, live_vault, live_yearn_router, live_vault_user, random_address, random_address_2):
    live_token.transfer(random_address, 10000, {"from": live_vault_user})
    live_token.approve(live_yearn_router, 10000, {"from": random_address})
    live_yearn_router.deposit(live_token, random_address, 10000, {
                              "from": random_address})

    live_vault.approve(live_yearn_router, live_vault.balanceOf(
        random_address), {"from": random_address})
    live_yearn_router.withdraw(live_token, random_address, 10000, {
                               "from": random_address})

    assert live_vault.balanceOf(random_address) == 0
    assert live_vault.balanceOf(live_yearn_router) == 0
    assert live_token.balanceOf(live_yearn_router) == 0
    # NOTE: Potential for tiny dust loss
    assert 10000 - 10 <= live_token.balanceOf(random_address) <= 10000


def test_withdraw_max_live(live_token, live_vault, live_yearn_router, live_vault_user, random_address, random_address_2):
    live_token.transfer(random_address, 10000, {"from": live_vault_user})
    live_token.approve(live_yearn_router, 10000, {"from": random_address})
    live_yearn_router.deposit(live_token, random_address, 10000, {
                              "from": random_address})

    live_vault.approve(live_yearn_router, live_vault.balanceOf(
        random_address), {"from": random_address})
    live_yearn_router.withdraw(live_token, random_address, {
                               "from": random_address})

    assert live_vault.balanceOf(random_address) == 0
    assert live_vault.balanceOf(live_yearn_router) == 0
    assert live_token.balanceOf(live_yearn_router) == 0
    # NOTE: Potential for tiny dust loss
    assert 10000 - 10 <= live_token.balanceOf(random_address) <= 10000


def test_withdraw_half_live(live_token, live_vault, live_yearn_router, live_vault_user, random_address, random_address_2):
    live_token.transfer(random_address, 10000, {"from": live_vault_user})
    live_token.approve(live_yearn_router, 10000, {"from": random_address})
    live_yearn_router.deposit(live_token, random_address, 10000, {
                              "from": random_address})

    live_vault.approve(live_yearn_router, live_vault.balanceOf(
        random_address), {"from": random_address})
    live_yearn_router.withdraw(live_token, random_address, 5000, {
                               "from": random_address})

    assert live_vault.balanceOf(live_yearn_router) == 0
    assert live_token.balanceOf(live_yearn_router) == 0
    # NOTE: Potential for tiny dust loss
    assert 5000 - 10 <= live_token.balanceOf(random_address) <= 5000


def test_withdraw_with_recipient_live(live_token, live_vault, live_yearn_router, live_vault_user, random_address, random_address_2):
    live_token.transfer(random_address, 10000, {"from": live_vault_user})
    live_token.approve(live_yearn_router, 10000, {"from": random_address})
    live_yearn_router.deposit(live_token, random_address, 10000, {
                              "from": random_address})

    live_vault.approve(live_yearn_router, live_vault.balanceOf(
        random_address), {"from": random_address})
    live_yearn_router.withdraw(live_token, random_address_2, 10000, {
                               "from": random_address})
    assert live_vault.balanceOf(random_address) == 0
    assert live_vault.balanceOf(random_address_2) == 0
    assert live_vault.balanceOf(live_yearn_router) == 0
    assert live_token.balanceOf(live_yearn_router) == 0
    # NOTE: Potential for tiny dust loss
    assert 10000 - 10 <= live_token.balanceOf(random_address_2) <= 10000


def test_withdraw_half_with_recipient_live(live_token, live_vault, live_yearn_router, live_vault_user, random_address, random_address_2):
    live_token.transfer(random_address, 10000, {"from": live_vault_user})
    live_token.approve(live_yearn_router, 10000, {"from": random_address})
    live_yearn_router.deposit(live_token, random_address, 10000, {
                              "from": random_address})

    live_vault.approve(live_yearn_router, live_vault.balanceOf(
        random_address), {"from": random_address})
    live_yearn_router.withdraw(live_token, random_address_2, 5000, {
                               "from": random_address})

    assert live_token.balanceOf(random_address) == 0
    assert live_vault.balanceOf(random_address_2) == 0
    assert live_vault.balanceOf(live_yearn_router) == 0
    assert live_token.balanceOf(live_yearn_router) == 0

    # NOTE: Potential for tiny dust loss
    assert 5000 - 10 <= live_token.balanceOf(random_address_2) <= 5000


def test_withdraw_max_with_recipient_live(live_token, live_vault, live_yearn_router, live_vault_user, random_address, random_address_2):
    live_token.transfer(random_address, 10000, {"from": live_vault_user})
    live_token.approve(live_yearn_router, 10000, {"from": random_address})
    live_yearn_router.deposit(live_token, random_address, 10000, {
                              "from": random_address})

    live_vault.approve(live_yearn_router, live_vault.balanceOf(
        random_address), {"from": random_address})
    live_yearn_router.withdraw(live_token, random_address_2, {
                               "from": random_address})
    assert live_vault.balanceOf(random_address) == 0
    assert live_vault.balanceOf(random_address_2) == 0
    assert live_vault.balanceOf(live_yearn_router) == 0
    assert live_token.balanceOf(live_yearn_router) == 0
    # NOTE: Potential for tiny dust loss
    assert 10000 - 10 <= live_token.balanceOf(random_address_2) <= 10000
