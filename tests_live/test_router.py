import brownie
import pytest


def test_config(token, vault, registry, yearn_router):
    assert yearn_router.registry() == registry
    assert registry.numVaults(token) > 0
    assert yearn_router.numVaults(token) > 0

    assert registry.latestVault(token) == vault
    assert yearn_router.latestVault(token) == vault


def test_setRegistry(user, owner, gov, yearn_router, create_registry):
    with brownie.reverts():
        yearn_router.setRegistry(user, {"from": user})

    # Cannot set to an invalid registry
    with brownie.reverts():
        yearn_router.setRegistry(user, {"from": owner})

    with brownie.reverts():
        yearn_router.setRegistry(user, {"from": gov})

    # yGov must be the gov on the new registry too
    new_registry = create_registry()
    new_registry.setGovernance(user, {"from": gov})
    new_registry.acceptGovernance({"from": user})
    with brownie.reverts():
        yearn_router.setRegistry(new_registry, {"from": owner})
    new_registry.setGovernance(gov, {"from": user})
    new_registry.acceptGovernance({"from": gov})

    yearn_router.setRegistry(new_registry, {"from": owner})


def test_transfer_ownership(user, owner, yearn_router, create_registry):
    assert yearn_router.owner() == owner
    with brownie.reverts():
        yearn_router.setRegistry(user, {"from": user})

    with brownie.reverts():
        yearn_router.transferOwnership(user, {"from": user})

    yearn_router.transferOwnership(user, {"from": owner})

    # new owner can set registry
    assert yearn_router.owner() == user
    new_registry = create_registry()
    yearn_router.setRegistry(new_registry, {"from": user})


def test_deposit(token, vault, yearn_router, user):
    assert token.balanceOf(user) == 10000
    assert token.balanceOf(yearn_router) == 0
    assert vault.balanceOf(user) == 0

    token.approve(yearn_router, 10000, {"from": user})
    tx_receipt = yearn_router.deposit(token, user, 10000, {"from": user})

    expected_balance = (10000 / vault.pricePerShare()) * (10**vault.decimals())

    assert vault.balanceOf(yearn_router) == 0
    assert token.balanceOf(yearn_router) == 0
    assert token.balanceOf(user) == 0
    assert vault.balanceOf(user) == expected_balance

    deposit_events = tx_receipt.events["Deposit"]
    assert len(deposit_events) == 1
    assert deposit_events["recipient"] == user.address
    assert deposit_events["vault"] == vault.address
    assert deposit_events["shares"] == expected_balance
    assert deposit_events["amount"] == 10000


def test_deposit_with_recipient(token, vault, yearn_router, user, random_address):
    assert token.balanceOf(user) == 10000
    assert token.balanceOf(random_address) == 0

    token.approve(yearn_router, 10000, {"from": user})
    tx_receipt = yearn_router.deposit(
        token, random_address, 10000, {"from": user})

    expected_balance = (10000 / vault.pricePerShare()) * (10**vault.decimals())

    assert vault.balanceOf(random_address) == expected_balance
    assert vault.balanceOf(user) == 0
    assert vault.balanceOf(yearn_router) == 0
    assert token.balanceOf(user) == 0
    assert token.balanceOf(yearn_router) == 0

    deposit_events = tx_receipt.events["Deposit"]
    assert len(deposit_events) == 1
    assert deposit_events["recipient"] == random_address.address
    assert deposit_events["vault"] == vault.address
    assert deposit_events["shares"] == expected_balance
    assert deposit_events["amount"] == 10000


@pytest.fixture(scope="module")
def vault_with_user_deposit(token, vault, yearn_router, user):
    token.approve(yearn_router, 10000, {"from": user})
    yearn_router.deposit(token, user, 10000, {"from": user})

    vault.approve(yearn_router, vault.balanceOf(user), {"from": user})
    yield vault


def test_vault_with_user_deposit_fixture(user, yearn_router, vault_with_user_deposit):
    vault = vault_with_user_deposit
    share_factor = 10**vault.decimals() / vault.pricePerShare()
    expected_balance = 10000 * share_factor
    assert vault.balanceOf(user) == expected_balance
    assert vault.allowance(user, yearn_router) == vault.balanceOf(user)


@pytest.mark.parametrize("withdraw_amount", [5000, 10000])
def test_withdraw(token, yearn_router, user, withdraw_amount, vault_with_user_deposit):
    vault = vault_with_user_deposit

    assert token.balanceOf(yearn_router) == 0

    user_vault_balance_before = vault.balanceOf(user)

    tx_receipt = yearn_router.withdraw(
        token, user, withdraw_amount, {"from": user})

    share_factor = 10**vault.decimals() / vault.pricePerShare()
    recipient_token_balance = token.balanceOf(user)
    user_vault_balance_after = vault.balanceOf(user)

    assert user_vault_balance_after == round(
        (10000 - withdraw_amount) * share_factor)
    assert token.balanceOf(yearn_router) == 0
    # NOTE: Potential for tiny dust loss
    assert withdraw_amount - 10 <= recipient_token_balance <= withdraw_amount

    withdraw_events = tx_receipt.events["Withdraw"]
    assert len(withdraw_events) == 1
    assert withdraw_events["recipient"] == user.address
    assert withdraw_events["vault"] == vault.address
    assert withdraw_events["shares"] == user_vault_balance_before - \
        user_vault_balance_after
    assert withdraw_events["amount"] == recipient_token_balance


def test_withdraw_all(token, yearn_router, user, vault_with_user_deposit):
    vault = vault_with_user_deposit
    assert token.balanceOf(yearn_router) == 0

    user_vault_balance_before = vault.balanceOf(user)

    tx_receipt = yearn_router.withdraw(token, user, {"from": user})

    recipient_token_balance = token.balanceOf(user)
    user_vault_balance_after = vault.balanceOf(user)

    assert user_vault_balance_after == 0
    assert token.balanceOf(yearn_router) == 0
    # NOTE: Potential for tiny dust loss
    assert 10000 - 10 <= recipient_token_balance <= 10000

    withdraw_events = tx_receipt.events["Withdraw"]
    assert len(withdraw_events) == 1
    assert withdraw_events["recipient"] == user.address
    assert withdraw_events["vault"] == vault.address
    assert withdraw_events["shares"] == user_vault_balance_before - \
        user_vault_balance_after
    assert withdraw_events["amount"] == recipient_token_balance


@pytest.mark.parametrize("withdraw_amount", [5000, 10000])
def test_withdraw_with_recipient(token, yearn_router, user, random_address,
                                 withdraw_amount, vault_with_user_deposit):
    vault = vault_with_user_deposit

    assert token.balanceOf(yearn_router) == 0

    user_vault_balance_before = vault.balanceOf(user)

    tx_receipt = yearn_router.withdraw(token, random_address,
                                       withdraw_amount, {"from": user})

    share_factor = 10**vault.decimals() / vault.pricePerShare()
    recipient_token_balance = token.balanceOf(random_address)
    user_vault_balance_after = vault.balanceOf(user)

    assert user_vault_balance_after == round(
        (10000 - withdraw_amount) * share_factor)
    assert vault.balanceOf(random_address) == 0
    assert vault.balanceOf(yearn_router) == 0
    assert token.balanceOf(yearn_router) == 0
    # NOTE: Potential for tiny dust loss
    assert withdraw_amount - \
        10 <= recipient_token_balance <= withdraw_amount

    withdraw_events = tx_receipt.events["Withdraw"]
    assert len(withdraw_events) == 1
    assert withdraw_events["recipient"] == random_address.address
    assert withdraw_events["vault"] == vault.address
    assert withdraw_events["shares"] == user_vault_balance_before - \
        user_vault_balance_after
    assert withdraw_events["amount"] == recipient_token_balance


def test_withdraw_all_with_recipient(token, yearn_router, random_address,
                                     user, vault_with_user_deposit):
    vault = vault_with_user_deposit

    assert token.balanceOf(yearn_router) == 0

    user_vault_balance_before = vault.balanceOf(user)

    tx_receipt = yearn_router.withdraw(token, random_address, {"from": user})

    recipient_token_balance = token.balanceOf(random_address)
    user_vault_balance_after = vault.balanceOf(user)

    assert user_vault_balance_after == 0
    assert vault.balanceOf(random_address) == 0
    assert vault.balanceOf(yearn_router) == 0
    assert token.balanceOf(yearn_router) == 0
    # NOTE: Potential for tiny dust loss
    assert 10000 - 10 <= token.balanceOf(random_address) <= 10000

    withdraw_events = tx_receipt.events["Withdraw"]
    assert len(withdraw_events) == 1
    assert withdraw_events["recipient"] == random_address.address
    assert withdraw_events["vault"] == vault.address
    assert withdraw_events["shares"] == user_vault_balance_before - \
        user_vault_balance_after
    assert withdraw_events["amount"] == recipient_token_balance


@pytest.mark.parametrize("withdraw_amount_divider", [2, 1])
def test_withdraw_shares(token, yearn_router, user,
                         withdraw_amount_divider, vault_with_user_deposit):
    vault = vault_with_user_deposit

    vault_id = yearn_router.numVaults(token) - 1

    user_vault_balance_before = vault.balanceOf(user)
    share_factor = 10**vault.decimals() / vault.pricePerShare()
    shares_amount = user_vault_balance_before / withdraw_amount_divider
    expected_amount = round(shares_amount / share_factor)

    tx_receipt = yearn_router.withdrawShares(
        token, user, shares_amount, vault_id, {"from": user})

    recipient_token_balance = token.balanceOf(user)

    assert vault.balanceOf(yearn_router) == 0
    assert vault.balanceOf(user) == user_vault_balance_before - shares_amount
    assert token.balanceOf(yearn_router) == 0
    # NOTE: Potential for tiny dust loss
    assert expected_amount - 10 <= recipient_token_balance <= expected_amount

    withdraw_events = tx_receipt.events["Withdraw"]
    assert len(withdraw_events) == 1
    assert withdraw_events["recipient"] == user.address
    assert withdraw_events["vault"] == vault.address
    assert withdraw_events["shares"] == shares_amount
    assert withdraw_events["amount"] == recipient_token_balance


@pytest.mark.parametrize("withdraw_amount_divider", [2, 1])
def test_withdraw_shares_with_recipient(token, yearn_router, user, random_address,
                                        withdraw_amount_divider, vault_with_user_deposit):
    vault = vault_with_user_deposit

    vault_id = yearn_router.numVaults(token) - 1

    user_vault_balance_before = vault.balanceOf(user)
    share_factor = 10**vault.decimals() / vault.pricePerShare()
    shares_amount = user_vault_balance_before / withdraw_amount_divider
    expected_amount = round(shares_amount / share_factor)

    tx_receipt = yearn_router.withdrawShares(
        token, random_address, shares_amount, vault_id, {"from": user})

    recipient_token_balance = token.balanceOf(random_address)

    assert vault.balanceOf(yearn_router) == 0
    assert vault.balanceOf(user) == user_vault_balance_before - shares_amount
    assert token.balanceOf(yearn_router) == 0
    assert token.balanceOf(user) == 0
    # NOTE: Potential for tiny dust loss
    assert expected_amount - 10 <= recipient_token_balance <= expected_amount

    withdraw_events = tx_receipt.events["Withdraw"]
    assert len(withdraw_events) == 1
    assert withdraw_events["recipient"] == random_address.address
    assert withdraw_events["vault"] == vault.address
    assert withdraw_events["shares"] == shares_amount
    assert withdraw_events["amount"] == recipient_token_balance


def test_withdraw_all_shares(token, yearn_router, user, vault_with_user_deposit):
    vault = vault_with_user_deposit
    vault_balance = vault.balanceOf(user)

    vault_id = yearn_router.numVaults(token) - 1
    tx_receipt = yearn_router.withdrawShares(
        token, user, vault_id, {"from": user})
    recipient_token_balance = token.balanceOf(user)

    assert vault.balanceOf(yearn_router) == 0
    assert vault.balanceOf(user) == 0
    assert token.balanceOf(yearn_router) == 0
    # NOTE: Potential for tiny dust loss
    assert 10000 - 10 <= recipient_token_balance <= 10000

    withdraw_events = tx_receipt.events["Withdraw"]
    assert len(withdraw_events) == 1
    assert withdraw_events["recipient"] == user.address
    assert withdraw_events["vault"] == vault.address
    assert withdraw_events["shares"] == vault_balance
    assert withdraw_events["amount"] == recipient_token_balance


def test_withdraw_all_shares_with_recipient(token, yearn_router, user,
                                            random_address, vault_with_user_deposit):
    vault = vault_with_user_deposit
    vault_balance = vault.balanceOf(user)

    vault_id = yearn_router.numVaults(token) - 1
    tx_receipt = yearn_router.withdrawShares(
        token, random_address, vault_id, {"from": user})
    recipient_token_balance = token.balanceOf(random_address)

    assert vault.balanceOf(yearn_router) == 0
    assert vault.balanceOf(user) == 0
    assert token.balanceOf(yearn_router) == 0
    assert token.balanceOf(user) == 0
    # NOTE: Potential for tiny dust loss
    assert 10000 - 10 <= recipient_token_balance <= 10000

    withdraw_events = tx_receipt.events["Withdraw"]
    assert len(withdraw_events) == 1
    assert withdraw_events["recipient"] == random_address.address
    assert withdraw_events["vault"] == vault.address
    assert withdraw_events["shares"] == vault_balance
    assert withdraw_events["amount"] == recipient_token_balance


def test_getVaultId(token, yearn_router, vaults, random_address):
    with brownie.reverts():
        yearn_router.getVaultId(token, random_address)

    with brownie.reverts():
        yearn_router.getVaultId(random_address, brownie.ZERO_ADDRESS)

    for index, vault_address in enumerate(vaults):
        vault_id = yearn_router.getVaultId(token, vault_address)
        assert vault_id == index
