import brownie

AMOUNT = 100


def test_config(gov, token, vault, registry, yearn_router, interface):
    # No vault added to the registry yet, so these methods should fail
    assert registry.numVaults(token) == 0

    with brownie.reverts():
        interface.RegistryAPI(yearn_router.registry()).latestVault(token)
        yearn_router.latestVault(token)

    # This won't revert though, there's no Vaults yet
    assert interface.RegistryAPI(
        yearn_router.registry()).numVaults(token) == 0
    assert yearn_router.numVaults(token) == 0

    # Now they work when we have a Vault
    registry.newRelease(vault, {"from": gov})
    registry.endorseVault(vault, {"from": gov})

    assert registry.numVaults(token) == 1
    assert interface.RegistryAPI(
        yearn_router.registry()).latestVault(token) == vault
    assert interface.RegistryAPI(
        yearn_router.registry()).numVaults(token) == 1
    assert interface.RegistryAPI(
        yearn_router.registry()).vaults(token, 0) == vault
    assert yearn_router.latestVault(token) == vault
    assert yearn_router.numVaults(token) == 1
    assert yearn_router.vaults(token, 0) == vault


def test_setRegistry(random_address, owner, gov, yearn_router, new_registry):
    with brownie.reverts():
        yearn_router.setRegistry(random_address, {"from": random_address})

    # Cannot set to an invalid registry
    with brownie.reverts():
        yearn_router.setRegistry(random_address, {"from": owner})

    with brownie.reverts():
        yearn_router.setRegistry(random_address, {"from": gov})

    # yGov must be the gov on the new registry too
    new_registry.setGovernance(random_address, {"from": gov})
    new_registry.acceptGovernance({"from": random_address})
    with brownie.reverts():
        yearn_router.setRegistry(new_registry, {"from": owner})
    new_registry.setGovernance(gov, {"from": random_address})
    new_registry.acceptGovernance({"from": gov})

    yearn_router.setRegistry(new_registry, {"from": owner})


def test_transfer_ownership(random_address, owner, yearn_router, new_registry):
    assert yearn_router.owner() == owner
    with brownie.reverts():
        yearn_router.setRegistry(random_address, {"from": random_address})

    with brownie.reverts():
        yearn_router.transferOwnership(
            random_address, {"from": random_address})

    yearn_router.transferOwnership(random_address, {"from": owner})

    # new owner can set registry
    assert yearn_router.owner() == random_address
    yearn_router.setRegistry(new_registry, {"from": random_address})


def test_deposit(token, registry, vault, yearn_router, gov, random_address):
    registry.newRelease(vault, {"from": gov})
    registry.endorseVault(vault, {"from": gov})
    token.transfer(random_address, 10000, {"from": gov})
    assert vault.balanceOf(
        random_address) == vault.balanceOf(yearn_router) == 0

    # transfer some random tokens to the router to ensure this doesn't effect any accounting
    # or the invariant check.
    token.transfer(yearn_router, 10000, {"from": gov})
    routerTokenBalance = token.balanceOf(yearn_router)
    assert routerTokenBalance == 10000

    token.approve(yearn_router, 10000, {"from": random_address})
    yearn_router.deposit(token, random_address, 10000,
                         {"from": random_address})

    assert vault.balanceOf(random_address) == 10000
    assert vault.balanceOf(yearn_router) == 0
    assert token.balanceOf(random_address) == 0
    assert token.balanceOf(yearn_router) == routerTokenBalance


def test_deposit_with_recipient(token, registry, vault, yearn_router, gov, random_address, random_address_2):
    registry.newRelease(vault, {"from": gov})
    registry.endorseVault(vault, {"from": gov})
    token.transfer(random_address, 10000, {"from": gov})
    assert vault.balanceOf(
        random_address) == vault.balanceOf(yearn_router) == 0

    # transfer some random tokens to the router to ensure this doesn't effect any accounting
    # or the invariant check.
    token.transfer(yearn_router, 10000, {"from": gov})
    routerTokenBalance = token.balanceOf(yearn_router)
    assert routerTokenBalance == 10000

    token.approve(yearn_router, 10000, {"from": random_address})
    yearn_router.deposit(token, random_address_2, 10000,
                         {"from": random_address})

    assert vault.balanceOf(random_address_2) == 10000
    assert vault.balanceOf(random_address) == 0

    assert vault.balanceOf(yearn_router) == 0
    assert token.balanceOf(random_address) == 0
    assert token.balanceOf(yearn_router) == routerTokenBalance


def test_withdraw_all(token, registry, vault, yearn_router, gov, random_address):
    registry.newRelease(vault, {"from": gov})
    registry.endorseVault(vault, {"from": gov})
    token.transfer(random_address, 1000000, {"from": gov})
    token.approve(yearn_router, 1000000, {"from": random_address})

    # transfer some random tokens to the router to ensure this doesn't effect any accounting
    # or the invariant check.
    token.transfer(yearn_router, 10000, {"from": gov})
    routerTokenBalance = token.balanceOf(yearn_router)
    assert routerTokenBalance == 10000

    yearn_router.deposit(token, random_address, 1000000,
                         {"from": random_address})

    vault.approve(yearn_router, vault.balanceOf(
        random_address), {"from": random_address})
    yearn_router.withdraw(token, random_address, 1000000,
                          {"from": random_address})

    assert token.balanceOf(yearn_router) == routerTokenBalance
    assert vault.balanceOf(yearn_router) == 0
    assert token.balanceOf(random_address) == 1000000


def test_withdraw_all_with_recipient(token, registry, vault, yearn_router, gov, random_address, random_address_2):
    registry.newRelease(vault, {"from": gov})
    registry.endorseVault(vault, {"from": gov})
    token.transfer(random_address, 1000000, {"from": gov})
    token.approve(yearn_router, 1000000, {"from": random_address})

    # transfer some random tokens to the router to ensure this doesn't effect any accounting
    # or the invariant check.
    token.transfer(yearn_router, 10000, {"from": gov})
    routerTokenBalance = token.balanceOf(yearn_router)
    assert routerTokenBalance == 10000

    yearn_router.deposit(token, random_address, 1000000,
                         {"from": random_address})

    vault.approve(yearn_router, vault.balanceOf(
        random_address), {"from": random_address})
    yearn_router.withdraw(token, random_address_2,
                          1000000, {"from": random_address})

    assert token.balanceOf(yearn_router) == routerTokenBalance
    assert vault.balanceOf(yearn_router) == 0
    assert token.balanceOf(random_address) == 0
    assert token.balanceOf(random_address_2) == 1000000


def test_withdraw_max(token, registry, vault, yearn_router, gov, random_address):
    registry.newRelease(vault, {"from": gov})
    registry.endorseVault(vault, {"from": gov})
    token.transfer(random_address, 10000, {"from": gov})
    token.approve(yearn_router, 10000, {"from": random_address})

    # transfer some random tokens to the router to ensure this doesn't effect any accounting
    # or the invariant check.
    token.transfer(yearn_router, 10000, {"from": gov})
    routerTokenBalance = token.balanceOf(yearn_router)
    assert routerTokenBalance == 10000

    yearn_router.deposit(token, random_address, 10000,
                         {"from": random_address})

    vault.approve(yearn_router, vault.balanceOf(
        random_address), {"from": random_address})
    yearn_router.withdraw(token, random_address, {"from": random_address})

    assert token.balanceOf(yearn_router) == routerTokenBalance
    assert vault.balanceOf(yearn_router) == 0
    assert token.balanceOf(random_address) == 10000


def test_withdraw_max_with_recipient(token, registry, vault, yearn_router, gov, random_address, random_address_2):
    registry.newRelease(vault, {"from": gov})
    registry.endorseVault(vault, {"from": gov})
    token.transfer(random_address, 10000, {"from": gov})
    token.approve(yearn_router, 10000, {"from": random_address})

    # transfer some random tokens to the router to ensure this doesn't effect any accounting
    # or the invariant check.
    token.transfer(yearn_router, 10000, {"from": gov})
    routerTokenBalance = token.balanceOf(yearn_router)
    assert routerTokenBalance == 10000

    yearn_router.deposit(token, random_address, 10000,
                         {"from": random_address})

    vault.approve(yearn_router, vault.balanceOf(
        random_address), {"from": random_address})
    yearn_router.withdraw(token, random_address_2, {"from": random_address})

    assert token.balanceOf(yearn_router) == routerTokenBalance
    assert vault.balanceOf(yearn_router) == 0
    assert token.balanceOf(random_address) == 0
    assert token.balanceOf(random_address_2) == 10000


def test_withdraw_half(token, registry, vault, yearn_router, gov, random_address):
    registry.newRelease(vault, {"from": gov})
    registry.endorseVault(vault, {"from": gov})
    token.transfer(random_address, 1000000, {"from": gov})
    token.approve(yearn_router, 1000000, {"from": random_address})
    yearn_router.deposit(token, random_address, 1000000,
                         {"from": random_address})

    # transfer some random tokens to the router to ensure this doesn't effect any accounting
    # or the invariant check.
    token.transfer(yearn_router, 10000, {"from": gov})
    routerTokenBalance = token.balanceOf(yearn_router)
    assert routerTokenBalance == 10000

    vault.approve(yearn_router, vault.balanceOf(
        random_address), {"from": random_address})
    yearn_router.withdraw(token, random_address, 500000,
                          {"from": random_address})

    assert token.balanceOf(random_address) == 500000
    assert token.balanceOf(yearn_router) == routerTokenBalance
    assert vault.balanceOf(yearn_router) == 0


def test_withdraw_multiple_vaults(token, registry, create_vault, yearn_router, gov, random_address, interface):
    vault1 = create_vault(releaseDelta=1, token=token)
    registry.newRelease(vault1, {"from": gov})
    registry.endorseVault(vault1, {"from": gov})

    token.transfer(random_address, 20000, {"from": gov})
    token.approve(yearn_router, 20000, {"from": random_address})

    # transfer some random tokens to the router to ensure this doesn't effect any accounting
    # or the invariant check.
    token.transfer(yearn_router, 10000, {"from": gov})
    routerTokenBalance = token.balanceOf(yearn_router)
    assert routerTokenBalance == 10000

    yearn_router.deposit(token, random_address, 10000,
                         {"from": random_address})

    assert vault1.balanceOf(random_address) == 10000

    vault2 = create_vault(releaseDelta=0, token=token)
    registry.newRelease(vault2, {"from": gov})
    registry.endorseVault(vault2, {"from": gov})

    assert interface.RegistryAPI(
        yearn_router.registry()).latestVault(token) == vault2
    assert yearn_router.latestVault(token) == vault2

    yearn_router.deposit(token, random_address, 10000,
                         {"from": random_address})

    assert vault1.balanceOf(random_address) == 10000
    assert vault2.balanceOf(random_address) == 10000

    vault1.approve(yearn_router,
                   vault1.balanceOf(random_address), {"from": random_address})
    vault2.approve(yearn_router,
                   vault2.balanceOf(random_address), {"from": random_address})

    yearn_router.withdraw(token, random_address, 15000,
                          {"from": random_address})

    assert token.balanceOf(random_address) == 15000
    assert vault2.balanceOf(random_address) == 5000
    assert vault1.balanceOf(random_address) == 0
    assert token.balanceOf(yearn_router) == routerTokenBalance
    assert vault1.balanceOf(yearn_router) == 0
    assert vault2.balanceOf(yearn_router) == 0


def test_migrate(token, registry, create_vault, yearn_router, gov, random_address, interface):
    vault1 = create_vault(releaseDelta=1, token=token)
    registry.newRelease(vault1, {"from": gov})
    registry.endorseVault(vault1, {"from": gov})

    # transfer some random tokens to the router to ensure this doesn't effect any accounting
    # or the invariant check.
    token.transfer(yearn_router, 10000, {"from": gov})
    routerTokenBalance = token.balanceOf(yearn_router)
    assert routerTokenBalance == 10000

    token.transfer(random_address, 10000, {"from": gov})
    token.approve(yearn_router, 10000, {"from": random_address})
    yearn_router.deposit(token, random_address, 10000,
                         {"from": random_address})

    assert vault1.balanceOf(random_address) == 10000

    vault2 = create_vault(releaseDelta=0, token=token)
    registry.newRelease(vault2, {"from": gov})
    registry.endorseVault(vault2, {"from": gov})

    assert interface.RegistryAPI(
        yearn_router.registry()).latestVault(token) == vault2
    assert yearn_router.latestVault(token) == vault2

    vault1.approve(yearn_router,
                   vault1.balanceOf(random_address), {"from": random_address})
    yearn_router.migrate(token, {"from": random_address})

    assert vault1.balanceOf(random_address) == 0
    assert vault2.balanceOf(random_address) == 10000
    assert vault1.balanceOf(yearn_router) == 0
    assert vault2.balanceOf(yearn_router) == 0
    assert token.balanceOf(yearn_router) == routerTokenBalance


def test_migrate_half(token, registry, create_vault, yearn_router, gov, random_address, interface):
    vault1 = create_vault(releaseDelta=1, token=token)
    registry.newRelease(vault1, {"from": gov})
    registry.endorseVault(vault1, {"from": gov})

    token.transfer(random_address, 10000, {"from": gov})
    token.approve(yearn_router, 10000, {"from": random_address})

    # transfer some random tokens to the router to ensure this doesn't effect any accounting
    # or the invariant check.
    token.transfer(yearn_router, 10000, {"from": gov})
    routerTokenBalance = token.balanceOf(yearn_router)
    assert routerTokenBalance == 10000

    yearn_router.deposit(token, random_address, 10000,
                         {"from": random_address})

    assert vault1.balanceOf(random_address) == 10000

    vault2 = create_vault(releaseDelta=0, token=token)
    registry.newRelease(vault2, {"from": gov})
    registry.endorseVault(vault2, {"from": gov})

    assert interface.RegistryAPI(
        yearn_router.registry()).latestVault(token) == vault2
    assert yearn_router.latestVault(token) == vault2

    vault1.approve(yearn_router,
                   vault1.balanceOf(random_address), {"from": random_address})
    yearn_router.migrate(token, 5000, {"from": random_address})

    assert vault1.balanceOf(random_address) == 5000
    assert vault2.balanceOf(random_address) == 5000
    assert vault1.balanceOf(yearn_router) == 0
    assert vault2.balanceOf(yearn_router) == 0
    assert token.balanceOf(yearn_router) == routerTokenBalance


def test_withdraw_with_direct_deposit(gov, token, create_vault, registry, yearn_router, random_address):
    # this test is meant to mimic a scenario where a user
    # deposits tokens directly into a vault (without our router)
    # and then attempts to withdraw through our router.
    # the tests specifically creates a new vault to ensure this would work
    # with any vault, even ones our router has never used / approved.
    vault1 = create_vault(releaseDelta=1, token=token)
    registry.newRelease(vault1, {"from": gov})
    registry.endorseVault(vault1, {"from": gov})

    token.transfer(random_address, 10000, {"from": gov})
    token.approve(vault1, 10000, {"from": random_address})
    vault1.deposit(10000, {"from": random_address})

    assert vault1.balanceOf(random_address) == 10000
    assert token.balanceOf(random_address) == 0

    # random_address deposited directly to the vault and now attempts to use our router to withdraw
    vault1.approve(yearn_router,
                   vault1.balanceOf(random_address), {"from": random_address})

    # transfer some random tokens to the router to ensure this doesn't effect any accounting
    # or the invariant check.
    token.transfer(yearn_router, 10000, {"from": gov})
    routerTokenBalance = token.balanceOf(yearn_router)
    assert routerTokenBalance == 10000

    yearn_router.withdraw(token, random_address, 10000,
                          {"from": random_address})

    # NOTE: based on this test no approval is required for the yearn vault to move the
    # vault tokens on a user's behalf.

    # random_address should have his tokens back
    assert vault1.balanceOf(random_address) == 0
    assert token.balanceOf(random_address) == 10000
    assert vault1.balanceOf(yearn_router) == 0
    assert token.balanceOf(yearn_router) == routerTokenBalance
    assert vault1.allowance(yearn_router, vault1) == 0
