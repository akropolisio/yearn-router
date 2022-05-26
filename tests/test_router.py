import brownie
import pytest


def test_config(token, create_token, vault, registry, yearn_router):
    assert yearn_router.registry() == registry

    assert registry.numVaults(token) == 1
    assert registry.latestVault(token) == vault
    assert registry.vaults(token, 0) == vault
    assert yearn_router.latestVault(token) == vault
    assert yearn_router.numVaults(token) == 1
    assert yearn_router.vaults(token, 0) == vault

    new_token = create_token()
    assert registry.numVaults(new_token) == 0
    assert yearn_router.numVaults(new_token) == 0

    with brownie.reverts():
        registry.latestVault(new_token)

    with brownie.reverts():
        yearn_router.latestVault(new_token)


def test_setRegistry(random_address, owner, gov, yearn_router, create_registry):
    with brownie.reverts():
        yearn_router.setRegistry(random_address, {"from": random_address})

    # Cannot set to an invalid registry
    with brownie.reverts():
        yearn_router.setRegistry(random_address, {"from": owner})

    with brownie.reverts():
        yearn_router.setRegistry(random_address, {"from": gov})

    # yGov must be the gov on the new registry too
    new_registry = create_registry()
    new_registry.setGovernance(random_address, {"from": gov})
    new_registry.acceptGovernance({"from": random_address})
    with brownie.reverts():
        yearn_router.setRegistry(new_registry, {"from": owner})
    new_registry.setGovernance(gov, {"from": random_address})
    new_registry.acceptGovernance({"from": gov})
    yearn_router.setRegistry(new_registry, {"from": owner})


def test_transfer_ownership(random_address, owner, yearn_router, create_registry):
    assert yearn_router.owner() == owner
    with brownie.reverts():
        yearn_router.setRegistry(random_address, {"from": random_address})

    with brownie.reverts():
        yearn_router.transferOwnership(
            random_address, {"from": random_address})

    yearn_router.transferOwnership(random_address, {"from": owner})

    # new owner can set registry
    assert yearn_router.owner() == random_address
    new_registry = create_registry()
    yearn_router.setRegistry(new_registry, {"from": random_address})


def test_deposit(token, vault, yearn_router, user):
    assert token.balanceOf(user) == 10000
    assert token.balanceOf(yearn_router) == 10000
    assert vault.balanceOf(user) == 0
    assert vault.balanceOf(yearn_router) == 0

    token.approve(yearn_router, 10000, {"from": user})
    tx_receipt = yearn_router.deposit(token, user, 10000, {"from": user})

    assert vault.balanceOf(user) == 10000
    assert vault.balanceOf(yearn_router) == 0
    assert token.balanceOf(user) == 0
    assert token.balanceOf(yearn_router) == 10000

    deposit_events = tx_receipt.events["Deposit"]
    assert len(deposit_events) == 1
    assert deposit_events["recipient"] == user.address
    assert deposit_events["vault"] == vault.address
    assert deposit_events["shares"] == 10000
    assert deposit_events["amount"] == 10000


def test_deposit_with_recipient(token, vault, yearn_router, user, random_address):
    assert token.balanceOf(user) == 10000
    assert token.balanceOf(yearn_router) == 10000
    assert token.balanceOf(random_address) == 0
    assert vault.balanceOf(user) == 0
    assert vault.balanceOf(yearn_router) == 0
    assert vault.balanceOf(random_address) == 0

    token.approve(yearn_router, 10000, {"from": user})
    tx_receipt = yearn_router.deposit(
        token, random_address, 10000, {"from": user})

    assert vault.balanceOf(random_address) == 10000
    assert vault.balanceOf(user) == 0
    assert vault.balanceOf(yearn_router) == 0

    assert token.balanceOf(user) == 0
    assert token.balanceOf(yearn_router) == 10000

    deposit_events = tx_receipt.events["Deposit"]
    assert len(deposit_events) == 1
    assert deposit_events["recipient"] == random_address.address
    assert deposit_events["vault"] == vault.address
    assert deposit_events["shares"] == 10000
    assert deposit_events["amount"] == 10000


@pytest.fixture
def vault_with_user_deposit(token, vault, yearn_router, user):
    token.approve(yearn_router, 10000, {"from": user})
    yearn_router.deposit(token, user, 10000, {"from": user})

    vault.approve(yearn_router, vault.balanceOf(user), {"from": user})
    yield vault


def test_vault_with_user_deposit_fixture(user, yearn_router, vault_with_user_deposit):
    vault = vault_with_user_deposit
    assert vault.balanceOf(user) == 10000
    assert vault.allowance(user, yearn_router) == 10000


@pytest.mark.parametrize("withdraw_amount", [5000, 10000])
def test_withdraw(token, yearn_router, user, withdraw_amount, vault_with_user_deposit):
    vault = vault_with_user_deposit

    tx_receipt = yearn_router.withdraw(
        token, user, withdraw_amount, {"from": user})

    assert token.balanceOf(yearn_router) == 10000
    assert token.balanceOf(user) == withdraw_amount
    assert vault.balanceOf(yearn_router) == 0
    assert vault.balanceOf(user) == 10000 - withdraw_amount

    withdraw_events = tx_receipt.events["Withdraw"]
    assert len(withdraw_events) == 1
    assert withdraw_events["recipient"] == user.address
    assert withdraw_events["vault"] == vault.address
    assert withdraw_events["shares"] == withdraw_amount
    assert withdraw_events["amount"] == withdraw_amount


@pytest.mark.parametrize("withdraw_amount", [5000, 10000])
def test_withdraw_with_recipient(token, yearn_router, user, random_address,
                                 vault_with_user_deposit, withdraw_amount):
    vault = vault_with_user_deposit

    tx_receipt = yearn_router.withdraw(token, random_address,
                                       withdraw_amount, {"from": user})

    assert token.balanceOf(yearn_router) == 10000
    assert token.balanceOf(user) == 0
    assert token.balanceOf(random_address) == withdraw_amount
    assert vault.balanceOf(yearn_router) == 0
    assert vault.balanceOf(user) == 10000 - withdraw_amount

    withdraw_events = tx_receipt.events["Withdraw"]
    assert len(withdraw_events) == 1
    assert withdraw_events["recipient"] == random_address.address
    assert withdraw_events["vault"] == vault.address
    assert withdraw_events["shares"] == withdraw_amount
    assert withdraw_events["amount"] == withdraw_amount


def test_withdraw_all(token, yearn_router, user, vault_with_user_deposit):
    vault = vault_with_user_deposit

    tx_receipt = yearn_router.withdraw(token, user, {"from": user})

    assert token.balanceOf(yearn_router) == 10000
    assert vault.balanceOf(yearn_router) == 0
    assert token.balanceOf(user) == 10000

    withdraw_events = tx_receipt.events["Withdraw"]
    assert len(withdraw_events) == 1
    assert withdraw_events["recipient"] == user.address
    assert withdraw_events["vault"] == vault.address
    assert withdraw_events["shares"] == 10000
    assert withdraw_events["amount"] == 10000


def test_withdraw_all_with_recipient(token, yearn_router, user, random_address, vault_with_user_deposit):
    vault = vault_with_user_deposit

    tx_receipt = yearn_router.withdraw(token, random_address, {"from": user})

    assert token.balanceOf(random_address) == 10000
    assert token.balanceOf(yearn_router) == 10000
    assert token.balanceOf(user) == 0
    assert vault.balanceOf(yearn_router) == 0

    withdraw_events = tx_receipt.events["Withdraw"]
    assert len(withdraw_events) == 1
    assert withdraw_events["recipient"] == random_address.address
    assert withdraw_events["vault"] == vault.address
    assert withdraw_events["shares"] == 10000
    assert withdraw_events["amount"] == 10000


def test_withdraw_multiple_vaults(token, registry, create_vault, yearn_router, user):
    vault1 = create_vault(token=token, version="1")

    token.approve(yearn_router, 10000, {"from": user})
    yearn_router.deposit(token, user, 5000, {"from": user})

    vault2 = create_vault(token=token, version="2")

    assert registry.latestVault(token) == vault2
    assert yearn_router.latestVault(token) == vault2

    yearn_router.deposit(token, user, 5000, {"from": user})

    assert vault1.balanceOf(user) == 5000
    assert vault2.balanceOf(user) == 5000

    vault1.approve(yearn_router, vault1.balanceOf(user), {"from": user})
    vault2.approve(yearn_router, vault2.balanceOf(user), {"from": user})

    tx_receipt = yearn_router.withdraw(token, user, 7500, {"from": user})
    assert token.balanceOf(user) == 7500
    assert vault2.balanceOf(user) == 2500
    assert vault1.balanceOf(user) == 0
    assert token.balanceOf(yearn_router) == 10000
    assert vault1.balanceOf(yearn_router) == 0
    assert vault2.balanceOf(yearn_router) == 0

    withdraw_events = tx_receipt.events["Withdraw"]
    assert len(withdraw_events) == 2
    assert withdraw_events[0]["recipient"] == user.address
    assert withdraw_events[0]["vault"] == vault1.address
    assert withdraw_events[0]["shares"] == 5000
    assert withdraw_events[0]["amount"] == 5000
    assert withdraw_events[1]["recipient"] == user.address
    assert withdraw_events[1]["vault"] == vault2.address
    assert withdraw_events[1]["shares"] == 2500
    assert withdraw_events[1]["amount"] == 2500


def test_migrate(token, registry, create_vault, yearn_router, user):
    vault1 = create_vault(token=token, version="1")

    token.approve(yearn_router, 10000, {"from": user})
    yearn_router.deposit(token, user, 10000, {"from": user})

    assert vault1.balanceOf(user) == 10000

    vault2 = create_vault(token=token, version="2")

    assert vault2.balanceOf(user) == 0

    assert registry.latestVault(token) == vault2
    assert yearn_router.latestVault(token) == vault2

    vault1.approve(yearn_router, vault1.balanceOf(user), {"from": user})
    tx_receipt = yearn_router.migrate(token, {"from": user})

    assert vault1.balanceOf(user) == 0
    assert vault1.balanceOf(yearn_router) == 0
    assert vault2.balanceOf(user) == 10000
    assert vault2.balanceOf(yearn_router) == 0
    assert token.balanceOf(yearn_router) == 10000

    withdraw_events = tx_receipt.events["Withdraw"]
    deposit_events = tx_receipt.events["Deposit"]
    assert len(withdraw_events) == 1
    assert withdraw_events["recipient"] == yearn_router.address
    assert withdraw_events["vault"] == vault1.address
    assert withdraw_events["shares"] == 10000
    assert withdraw_events["amount"] == 10000

    assert len(deposit_events) == 1
    assert deposit_events["recipient"] == user.address
    assert deposit_events["vault"] == vault2.address
    assert deposit_events["shares"] == 10000
    assert deposit_events["amount"] == 10000


def test_migrate_half(token, registry, create_vault, yearn_router, user):
    vault1 = create_vault(token=token, version="1")

    token.approve(yearn_router, 10000, {"from": user})
    yearn_router.deposit(token, user, 10000, {"from": user})

    assert vault1.balanceOf(user) == 10000

    vault2 = create_vault(token=token, version="2")

    assert vault2.balanceOf(user) == 0

    assert registry.latestVault(token) == vault2
    assert yearn_router.latestVault(token) == vault2

    vault1.approve(yearn_router, vault1.balanceOf(user), {"from": user})
    tx_receipt = yearn_router.migrate(token, 5000, {"from": user})

    assert vault1.balanceOf(user) == 5000
    assert vault1.balanceOf(yearn_router) == 0
    assert vault2.balanceOf(user) == 5000
    assert vault2.balanceOf(yearn_router) == 0
    assert token.balanceOf(yearn_router) == 10000

    withdraw_events = tx_receipt.events["Withdraw"]
    deposit_events = tx_receipt.events["Deposit"]
    assert len(withdraw_events) == 1
    assert withdraw_events["recipient"] == yearn_router.address
    assert withdraw_events["vault"] == vault1.address
    assert withdraw_events["shares"] == 5000
    assert withdraw_events["amount"] == 5000

    assert len(deposit_events) == 1
    assert deposit_events["recipient"] == user.address
    assert deposit_events["vault"] == vault2.address
    assert deposit_events["shares"] == 5000
    assert deposit_events["amount"] == 5000


def test_withdraw_with_direct_deposit(token, vault, yearn_router, user):
    assert token.balanceOf(user) == 10000
    assert token.balanceOf(yearn_router) == 10000
    # this test is meant to mimic a scenario where a user
    # deposits tokens directly into a vault (without our router)
    # and then attempts to withdraw through our router.
    # the tests specifically creates a new vault to ensure this would work
    # with any vault, even ones our router has never used / approved.
    token.approve(vault, 10000, {"from": user})
    vault.deposit(10000, {"from": user})

    assert vault.balanceOf(user) == 10000
    assert token.balanceOf(user) == 0

    # user deposited directly to the vault and now attempts to use our router to withdraw
    vault.approve(yearn_router, vault.balanceOf(user), {"from": user})

    yearn_router.withdraw(token, user, 10000, {"from": user})

    # NOTE: based on this test no approval is required for the yearn vault to move the
    # vault tokens on a user's behalf.

    # user should have his tokens back
    assert vault.balanceOf(user) == 0
    assert vault.balanceOf(yearn_router) == 0
    assert vault.allowance(yearn_router, vault) == 0
    assert token.balanceOf(user) == 10000
    assert token.balanceOf(yearn_router) == 10000


@pytest.mark.parametrize("withdraw_amount_divider", [2, 1])
def test_withdraw_shares(token, yearn_router, user,
                         withdraw_amount_divider, vault_with_user_deposit):
    vault = vault_with_user_deposit

    vault_id = yearn_router.numVaults(token) - 1

    before_user_vault_balance = vault.balanceOf(user)
    share_factor = 10**vault.decimals() / vault.pricePerShare()
    shares_amount = before_user_vault_balance / withdraw_amount_divider
    expected_amount = round(shares_amount / share_factor)

    tx_receipt = yearn_router.withdrawShares(
        token, user, shares_amount, vault_id, {"from": user})

    assert vault.balanceOf(yearn_router) == 0
    assert vault.balanceOf(user) == before_user_vault_balance - shares_amount
    assert token.balanceOf(yearn_router) == 10000
    # NOTE: Potential for tiny dust loss
    assert expected_amount - 10 <= token.balanceOf(
        user) <= expected_amount

    withdraw_events = tx_receipt.events["Withdraw"]
    assert len(withdraw_events) == 1
    assert withdraw_events["recipient"] == user.address
    assert withdraw_events["vault"] == vault.address
    assert withdraw_events["shares"] == shares_amount
    assert withdraw_events["amount"] == token.balanceOf(user)


@pytest.mark.parametrize("withdraw_amount_divider", [2, 1])
def test_withdraw_shares_with_recipient(token, yearn_router, user, random_address,
                                        withdraw_amount_divider, vault_with_user_deposit):
    vault = vault_with_user_deposit

    vault_id = yearn_router.numVaults(token) - 1

    before_user_vault_balance = vault.balanceOf(user)
    share_factor = 10**vault.decimals() / vault.pricePerShare()
    shares_amount = before_user_vault_balance / withdraw_amount_divider
    expected_amount = round(shares_amount / share_factor)

    tx_receipt = yearn_router.withdrawShares(
        token, random_address, shares_amount, vault_id, {"from": user})

    assert vault.balanceOf(yearn_router) == 0
    assert vault.balanceOf(user) == before_user_vault_balance - shares_amount
    assert token.balanceOf(yearn_router) == 10000
    assert token.balanceOf(user) == 0
    # NOTE: Potential for tiny dust loss
    assert expected_amount - 10 <= token.balanceOf(
        random_address) <= expected_amount

    withdraw_events = tx_receipt.events["Withdraw"]
    assert len(withdraw_events) == 1
    assert withdraw_events["recipient"] == random_address.address
    assert withdraw_events["vault"] == vault.address
    assert withdraw_events["shares"] == shares_amount
    assert withdraw_events["amount"] == token.balanceOf(random_address)


def test_withdraw_all_shares(token, yearn_router, user, vault_with_user_deposit):
    vault = vault_with_user_deposit

    vault_id = yearn_router.numVaults(token) - 1
    tx_receipt = yearn_router.withdrawShares(
        token, user, vault_id, {"from": user})

    assert vault.balanceOf(yearn_router) == 0
    assert vault.balanceOf(user) == 0
    assert token.balanceOf(yearn_router) == 10000
    # NOTE: Potential for tiny dust loss
    assert 10000 - 10 <= token.balanceOf(user) <= 10000

    withdraw_events = tx_receipt.events["Withdraw"]
    assert len(withdraw_events) == 1
    assert withdraw_events["recipient"] == user.address
    assert withdraw_events["vault"] == vault.address
    assert withdraw_events["shares"] == 10000
    assert withdraw_events["amount"] == token.balanceOf(user)


def test_withdraw_all_shares_with_recipient(token, yearn_router, user,
                                            random_address, vault_with_user_deposit):
    vault = vault_with_user_deposit

    vault_id = yearn_router.numVaults(token) - 1
    tx_receipt = yearn_router.withdrawShares(
        token, random_address, vault_id, {"from": user})

    assert vault.balanceOf(yearn_router) == 0
    assert vault.balanceOf(user) == 0
    assert token.balanceOf(yearn_router) == 10000
    assert token.balanceOf(user) == 0
    # NOTE: Potential for tiny dust loss
    assert 10000 - 10 <= token.balanceOf(random_address) <= 10000

    withdraw_events = tx_receipt.events["Withdraw"]
    assert len(withdraw_events) == 1
    assert withdraw_events["recipient"] == random_address.address
    assert withdraw_events["vault"] == vault.address
    assert withdraw_events["shares"] == 10000
    assert withdraw_events["amount"] == token.balanceOf(random_address)
