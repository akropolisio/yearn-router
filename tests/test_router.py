import brownie

AMOUNT = 100


def test_config(gov, token, vault, registry, shape_shift_router, interface):
    # No vault added to the registry yet, so these methods should fail
    assert registry.numVaults(token) == 0

    with brownie.reverts():
        interface.RegistryAPI(shape_shift_router.registry()).latestVault(token)
        shape_shift_router.latestVault(token)

    # This won't revert though, there's no Vaults yet
    assert interface.RegistryAPI(
        shape_shift_router.registry()).numVaults(token) == 0
    assert shape_shift_router.numVaults(token) == 0

    # Now they work when we have a Vault
    registry.newRelease(vault, {"from": gov})
    registry.endorseVault(vault, {"from": gov})

    assert registry.numVaults(token) == 1
    assert interface.RegistryAPI(
        shape_shift_router.registry()).latestVault(token) == vault
    assert interface.RegistryAPI(
        shape_shift_router.registry()).numVaults(token) == 1
    assert interface.RegistryAPI(
        shape_shift_router.registry()).vaults(token, 0) == vault
    assert shape_shift_router.latestVault(token) == vault
    assert shape_shift_router.numVaults(token) == 1
    assert shape_shift_router.vaults(token, 0) == vault


def test_setRegistry(rando, affiliate, gov, shape_shift_router, new_registry):
    with brownie.reverts():
        shape_shift_router.setRegistry(rando, {"from": rando})

    # Cannot set to an invalid registry
    with brownie.reverts():
        shape_shift_router.setRegistry(rando, {"from": affiliate})

    with brownie.reverts():
        shape_shift_router.setRegistry(rando, {"from": gov})

    # yGov must be the gov on the new registry too
    new_registry.setGovernance(rando, {"from": gov})
    new_registry.acceptGovernance({"from": rando})
    with brownie.reverts():
        shape_shift_router.setRegistry(new_registry, {"from": affiliate})
    new_registry.setGovernance(gov, {"from": rando})
    new_registry.acceptGovernance({"from": gov})

    shape_shift_router.setRegistry(new_registry, {"from": affiliate})


def test_transfer_ownership(rando, affiliate, shape_shift_router, new_registry):
    assert shape_shift_router.owner() == affiliate
    with brownie.reverts():
        shape_shift_router.setRegistry(rando, {"from": rando})

    with brownie.reverts():
        shape_shift_router.transferOwnership(rando, {"from": rando})

    shape_shift_router.transferOwnership(rando, {"from": affiliate})

    # new owner can set registry
    assert shape_shift_router.owner() == rando
    shape_shift_router.setRegistry(new_registry, {"from": rando})


def test_deposit(token, registry, vault, shape_shift_router, gov, rando):
    registry.newRelease(vault, {"from": gov})
    registry.endorseVault(vault, {"from": gov})
    token.transfer(rando, 10000, {"from": gov})
    assert vault.balanceOf(rando) == vault.balanceOf(shape_shift_router) == 0

    # transfer some random tokens to the router to ensure this doesn't effect any accounting
    # or the invariant check.
    token.transfer(shape_shift_router, 10000, {"from": gov})
    routerTokenBalance = token.balanceOf(shape_shift_router)
    assert routerTokenBalance == 10000

    token.approve(shape_shift_router, 10000, {"from": rando})
    shape_shift_router.deposit(token, rando, 10000, {"from": rando})

    assert vault.balanceOf(rando) == 10000
    assert vault.balanceOf(shape_shift_router) == 0
    assert token.balanceOf(rando) == 0
    assert token.balanceOf(shape_shift_router) == routerTokenBalance


def test_deposit_with_recipient(token, registry, vault, shape_shift_router, gov, rando, rando2):
    registry.newRelease(vault, {"from": gov})
    registry.endorseVault(vault, {"from": gov})
    token.transfer(rando, 10000, {"from": gov})
    assert vault.balanceOf(rando) == vault.balanceOf(shape_shift_router) == 0

    # transfer some random tokens to the router to ensure this doesn't effect any accounting
    # or the invariant check.
    token.transfer(shape_shift_router, 10000, {"from": gov})
    routerTokenBalance = token.balanceOf(shape_shift_router)
    assert routerTokenBalance == 10000

    token.approve(shape_shift_router, 10000, {"from": rando})
    shape_shift_router.deposit(token, rando2, 10000, {"from": rando})

    assert vault.balanceOf(rando2) == 10000
    assert vault.balanceOf(rando) == 0

    assert vault.balanceOf(shape_shift_router) == 0
    assert token.balanceOf(rando) == 0
    assert token.balanceOf(shape_shift_router) == routerTokenBalance


def test_withdraw_all(token, registry, vault, shape_shift_router, gov, rando):
    registry.newRelease(vault, {"from": gov})
    registry.endorseVault(vault, {"from": gov})
    token.transfer(rando, 1000000, {"from": gov})
    token.approve(shape_shift_router, 1000000, {"from": rando})

    # transfer some random tokens to the router to ensure this doesn't effect any accounting
    # or the invariant check.
    token.transfer(shape_shift_router, 10000, {"from": gov})
    routerTokenBalance = token.balanceOf(shape_shift_router)
    assert routerTokenBalance == 10000

    shape_shift_router.deposit(token, rando, 1000000, {"from": rando})

    vault.approve(shape_shift_router, vault.balanceOf(rando), {"from": rando})
    shape_shift_router.withdraw(token, rando, 1000000, {"from": rando})

    assert token.balanceOf(shape_shift_router) == routerTokenBalance
    assert vault.balanceOf(shape_shift_router) == 0
    assert token.balanceOf(rando) == 1000000


def test_withdraw_all_with_recipient(token, registry, vault, shape_shift_router, gov, rando, rando2):
    registry.newRelease(vault, {"from": gov})
    registry.endorseVault(vault, {"from": gov})
    token.transfer(rando, 1000000, {"from": gov})
    token.approve(shape_shift_router, 1000000, {"from": rando})

    # transfer some random tokens to the router to ensure this doesn't effect any accounting
    # or the invariant check.
    token.transfer(shape_shift_router, 10000, {"from": gov})
    routerTokenBalance = token.balanceOf(shape_shift_router)
    assert routerTokenBalance == 10000

    shape_shift_router.deposit(token, rando, 1000000, {"from": rando})

    vault.approve(shape_shift_router, vault.balanceOf(rando), {"from": rando})
    shape_shift_router.withdraw(token, rando2, 1000000, {"from": rando})

    assert token.balanceOf(shape_shift_router) == routerTokenBalance
    assert vault.balanceOf(shape_shift_router) == 0
    assert token.balanceOf(rando) == 0
    assert token.balanceOf(rando2) == 1000000


def test_withdraw_max(token, registry, vault, shape_shift_router, gov, rando):
    registry.newRelease(vault, {"from": gov})
    registry.endorseVault(vault, {"from": gov})
    token.transfer(rando, 10000, {"from": gov})
    token.approve(shape_shift_router, 10000, {"from": rando})

    # transfer some random tokens to the router to ensure this doesn't effect any accounting
    # or the invariant check.
    token.transfer(shape_shift_router, 10000, {"from": gov})
    routerTokenBalance = token.balanceOf(shape_shift_router)
    assert routerTokenBalance == 10000

    shape_shift_router.deposit(token, rando, 10000, {"from": rando})

    vault.approve(shape_shift_router, vault.balanceOf(rando), {"from": rando})
    shape_shift_router.withdraw(token, rando, {"from": rando})

    assert token.balanceOf(shape_shift_router) == routerTokenBalance
    assert vault.balanceOf(shape_shift_router) == 0
    assert token.balanceOf(rando) == 10000


def test_withdraw_max_with_recipient(token, registry, vault, shape_shift_router, gov, rando, rando2):
    registry.newRelease(vault, {"from": gov})
    registry.endorseVault(vault, {"from": gov})
    token.transfer(rando, 10000, {"from": gov})
    token.approve(shape_shift_router, 10000, {"from": rando})

    # transfer some random tokens to the router to ensure this doesn't effect any accounting
    # or the invariant check.
    token.transfer(shape_shift_router, 10000, {"from": gov})
    routerTokenBalance = token.balanceOf(shape_shift_router)
    assert routerTokenBalance == 10000

    shape_shift_router.deposit(token, rando, 10000, {"from": rando})

    vault.approve(shape_shift_router, vault.balanceOf(rando), {"from": rando})
    shape_shift_router.withdraw(token, rando2, {"from": rando})

    assert token.balanceOf(shape_shift_router) == routerTokenBalance
    assert vault.balanceOf(shape_shift_router) == 0
    assert token.balanceOf(rando) == 0
    assert token.balanceOf(rando2) == 10000


def test_withdraw_half(token, registry, vault, shape_shift_router, gov, rando):
    registry.newRelease(vault, {"from": gov})
    registry.endorseVault(vault, {"from": gov})
    token.transfer(rando, 1000000, {"from": gov})
    token.approve(shape_shift_router, 1000000, {"from": rando})
    shape_shift_router.deposit(token, rando, 1000000, {"from": rando})

    # transfer some random tokens to the router to ensure this doesn't effect any accounting
    # or the invariant check.
    token.transfer(shape_shift_router, 10000, {"from": gov})
    routerTokenBalance = token.balanceOf(shape_shift_router)
    assert routerTokenBalance == 10000

    vault.approve(shape_shift_router, vault.balanceOf(rando), {"from": rando})
    shape_shift_router.withdraw(token, rando, 500000, {"from": rando})

    assert token.balanceOf(rando) == 500000
    assert token.balanceOf(shape_shift_router) == routerTokenBalance
    assert vault.balanceOf(shape_shift_router) == 0


def test_withdraw_multiple_vaults(token, registry, create_vault, shape_shift_router, gov, rando, interface):
    vault1 = create_vault(releaseDelta=1, token=token)
    registry.newRelease(vault1, {"from": gov})
    registry.endorseVault(vault1, {"from": gov})

    token.transfer(rando, 20000, {"from": gov})
    token.approve(shape_shift_router, 20000, {"from": rando})

    # transfer some random tokens to the router to ensure this doesn't effect any accounting
    # or the invariant check.
    token.transfer(shape_shift_router, 10000, {"from": gov})
    routerTokenBalance = token.balanceOf(shape_shift_router)
    assert routerTokenBalance == 10000

    shape_shift_router.deposit(token, rando, 10000, {"from": rando})

    assert vault1.balanceOf(rando) == 10000

    vault2 = create_vault(releaseDelta=0, token=token)
    registry.newRelease(vault2, {"from": gov})
    registry.endorseVault(vault2, {"from": gov})

    assert interface.RegistryAPI(
        shape_shift_router.registry()).latestVault(token) == vault2
    assert shape_shift_router.latestVault(token) == vault2

    shape_shift_router.deposit(token, rando, 10000, {"from": rando})

    assert vault1.balanceOf(rando) == 10000
    assert vault2.balanceOf(rando) == 10000

    vault1.approve(shape_shift_router,
                   vault1.balanceOf(rando), {"from": rando})
    vault2.approve(shape_shift_router,
                   vault2.balanceOf(rando), {"from": rando})

    shape_shift_router.withdraw(token, rando, 15000, {"from": rando})

    assert token.balanceOf(rando) == 15000
    assert vault2.balanceOf(rando) == 5000
    assert vault1.balanceOf(rando) == 0
    assert token.balanceOf(shape_shift_router) == routerTokenBalance
    assert vault1.balanceOf(shape_shift_router) == 0
    assert vault2.balanceOf(shape_shift_router) == 0


def test_migrate(token, registry, create_vault, shape_shift_router, gov, rando, interface):
    vault1 = create_vault(releaseDelta=1, token=token)
    registry.newRelease(vault1, {"from": gov})
    registry.endorseVault(vault1, {"from": gov})

    # transfer some random tokens to the router to ensure this doesn't effect any accounting
    # or the invariant check.
    token.transfer(shape_shift_router, 10000, {"from": gov})
    routerTokenBalance = token.balanceOf(shape_shift_router)
    assert routerTokenBalance == 10000

    token.transfer(rando, 10000, {"from": gov})
    token.approve(shape_shift_router, 10000, {"from": rando})
    shape_shift_router.deposit(token, rando, 10000, {"from": rando})

    assert vault1.balanceOf(rando) == 10000

    vault2 = create_vault(releaseDelta=0, token=token)
    registry.newRelease(vault2, {"from": gov})
    registry.endorseVault(vault2, {"from": gov})

    assert interface.RegistryAPI(
        shape_shift_router.registry()).latestVault(token) == vault2
    assert shape_shift_router.latestVault(token) == vault2

    vault1.approve(shape_shift_router,
                   vault1.balanceOf(rando), {"from": rando})
    shape_shift_router.migrate(token, {"from": rando})

    assert vault1.balanceOf(rando) == 0
    assert vault2.balanceOf(rando) == 10000
    assert vault1.balanceOf(shape_shift_router) == 0
    assert vault2.balanceOf(shape_shift_router) == 0
    assert token.balanceOf(shape_shift_router) == routerTokenBalance


def test_migrate_half(token, registry, create_vault, shape_shift_router, gov, rando, interface):
    vault1 = create_vault(releaseDelta=1, token=token)
    registry.newRelease(vault1, {"from": gov})
    registry.endorseVault(vault1, {"from": gov})

    token.transfer(rando, 10000, {"from": gov})
    token.approve(shape_shift_router, 10000, {"from": rando})

    # transfer some random tokens to the router to ensure this doesn't effect any accounting
    # or the invariant check.
    token.transfer(shape_shift_router, 10000, {"from": gov})
    routerTokenBalance = token.balanceOf(shape_shift_router)
    assert routerTokenBalance == 10000

    shape_shift_router.deposit(token, rando, 10000, {"from": rando})

    assert vault1.balanceOf(rando) == 10000

    vault2 = create_vault(releaseDelta=0, token=token)
    registry.newRelease(vault2, {"from": gov})
    registry.endorseVault(vault2, {"from": gov})

    assert interface.RegistryAPI(
        shape_shift_router.registry()).latestVault(token) == vault2
    assert shape_shift_router.latestVault(token) == vault2

    vault1.approve(shape_shift_router,
                   vault1.balanceOf(rando), {"from": rando})
    shape_shift_router.migrate(token, 5000, {"from": rando})

    assert vault1.balanceOf(rando) == 5000
    assert vault2.balanceOf(rando) == 5000
    assert vault1.balanceOf(shape_shift_router) == 0
    assert vault2.balanceOf(shape_shift_router) == 0
    assert token.balanceOf(shape_shift_router) == routerTokenBalance


def test_withdraw_with_direct_deposit(gov, token, create_vault, registry, shape_shift_router, rando):
    # this test is meant to mimic a scenario where a user
    # deposits tokens directly into a vault (without our router)
    # and then attempts to withdraw through our router.
    # the tests specifically creates a new vault to ensure this would work
    # with any vault, even ones our router has never used / approved.
    vault1 = create_vault(releaseDelta=1, token=token)
    registry.newRelease(vault1, {"from": gov})
    registry.endorseVault(vault1, {"from": gov})

    token.transfer(rando, 10000, {"from": gov})
    token.approve(vault1, 10000, {"from": rando})
    vault1.deposit(10000, {"from": rando})

    assert vault1.balanceOf(rando) == 10000
    assert token.balanceOf(rando) == 0

    # rando deposited directly to the vault and now attempts to use our router to withdraw
    vault1.approve(shape_shift_router,
                   vault1.balanceOf(rando), {"from": rando})

    # transfer some random tokens to the router to ensure this doesn't effect any accounting
    # or the invariant check.
    token.transfer(shape_shift_router, 10000, {"from": gov})
    routerTokenBalance = token.balanceOf(shape_shift_router)
    assert routerTokenBalance == 10000

    shape_shift_router.withdraw(token, rando, 10000, {"from": rando})

    # NOTE: based on this test no approval is required for the yearn vault to move the
    # vault tokens on a user's behalf.

    # rando should have his tokens back
    assert vault1.balanceOf(rando) == 0
    assert token.balanceOf(rando) == 10000
    assert vault1.balanceOf(shape_shift_router) == 0
    assert token.balanceOf(shape_shift_router) == routerTokenBalance
    assert vault1.allowance(shape_shift_router, vault1) == 0
